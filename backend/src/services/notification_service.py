"""
Notification Service Layer
Kakao AlimTalk sending logic migrated from PHP
"""
from typing import Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
import httpx

from src.repositories.notification_repository import NotificationRepository

KST = ZoneInfo("Asia/Seoul")
from src.models.notification_log_model import RecipientType, SendStatus
from src.models.notification_template_model import NotificationChannel
from src.config.settings import settings
from src.common.logging import logger, get_logger_with_request_id
from src.exceptions.custom_exceptions import ValidationError, BaseAppException


class NotificationService:
    """Kakao AlimTalk Service"""

    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo
        self.host_url = settings.kakao_alarm_url
        self.api_key = settings.kakao_alarm_key
        self.site_id = settings.kakao_alarm_site_id

    async def _send_kakao_alimtalk(
        self,
        template_id: str,
        tel_num: str,
        msg_content: str,
        sms_content: str,
        url_pc: str = "",
        url_mobile: str = "",
    ) -> Dict[str, Any]:
        """
        Send Kakao AlimTalk (migrated from PHP sendSMS method)

        Args:
            template_id: Template ID
            tel_num: Phone number
            msg_content: Message content
            sms_content: SMS fallback content
            url_pc: PC URL
            url_mobile: Mobile URL

        Returns:
            dict: {
                "is_success": bool,
                "no": str,
                "code": str,
                "content": str,
                "template": str
            }
        """
        log = get_logger_with_request_id()

        # Configuration validation
        if not self.host_url or not self.api_key or not self.site_id:
            log.error("Kakao AlimTalk configuration missing")
            raise ValidationError("Kakao AlimTalk configuration missing")

        # Generate message number (timestamp)
        current_time = datetime.now(KST).strftime("%Y%m%d%H%M%S")
        no = current_time

        # Prepare request data
        data = {
            "userid": self.site_id,
            "api_key": self.api_key,
            "template_id": template_id,
            "messages": [
                {
                    "no": no,
                    "tel_num": tel_num,
                    "msg_content": msg_content,
                    "sms_content": sms_content,
                    "use_sms": 1,
                    "btn_url": [
                        {
                            "url_pc": url_pc,
                            "url_mobile": url_mobile
                        }
                    ]
                }
            ]
        }

        log.info("Sending Kakao AlimTalk", template_id=template_id, tel_num=tel_num)

        try:
            # HTTP POST request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.host_url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                )

            response_data = response.json()
            code = response_data.get("code", "")

            # Success check (code == 0 or code == "0")
            is_success = (code == 0 or code == "0")

            result = {
                "is_success": is_success,
                "no": no,
                "code": code,
                "content": msg_content,
                "template": template_id
            }

            if is_success:
                log.info("Kakao AlimTalk sent successfully", no=no, code=code)
            else:
                log.warning("Kakao AlimTalk send failed", no=no, code=code, response=response_data)

            return result

        except httpx.RequestError as e:
            log.error("Kakao AlimTalk HTTP request failed", error=str(e))
            return {
                "is_success": False,
                "no": no,
                "code": "HTTP_ERROR",
                "content": msg_content,
                "template": template_id
            }
        except Exception as e:
            log.error("Kakao AlimTalk unexpected error", error=str(e))
            return {
                "is_success": False,
                "no": no,
                "code": "UNKNOWN_ERROR",
                "content": msg_content,
                "template": template_id
            }

    async def _create_and_send(
        self,
        recipient_type: RecipientType,
        recipient_id: str,
        phone: str,
        template_id: str,
        msg_content: str,
        pc_link: str = "",
        mo_link: str = ""
    ) -> Dict[str, Any]:
        """
        Create log + Send Kakao AlimTalk + Update log status

        Args:
            recipient_type: Recipient type (USER/COUNSELOR)
            recipient_id: Recipient ID
            phone: Phone number
            template_id: Template ID
            msg_content: Message content
            pc_link: PC link
            mo_link: Mobile link

        Returns:
            dict: Send result
        """
        log = get_logger_with_request_id()

        # 1. Create log
        notification_log = await self.notification_repo.create_log(
            recipient_type=recipient_type,
            recipient_id=recipient_id,
            channel=NotificationChannel.KAKAO,
            content=msg_content,
            template_id=int(template_id),
            title=None,
            variables={"template_id": template_id, "phone": phone}
        )

        # 2. Send Kakao AlimTalk
        result = await self._send_kakao_alimtalk(
            template_id=template_id,
            tel_num=phone,
            msg_content=msg_content,
            sms_content=msg_content.strip(),
            url_pc=pc_link,
            url_mobile=mo_link
        )

        # 3. Update log status
        if result["is_success"]:
            await self.notification_repo.update_log_status(
                log_id=notification_log.log_id,
                send_status=SendStatus.SUCCESS,
                provider_response=result
            )
        else:
            await self.notification_repo.update_log_status(
                log_id=notification_log.log_id,
                send_status=SendStatus.FAILED,
                provider_response=result,
                failed_reason=f"Code: {result['code']}",
                increment_retry=False
            )

        # 4. Commit DB
        await self.notification_repo.db.commit()

        log.info("Notification sent and logged",
                log_id=notification_log.log_id,
                is_success=result["is_success"],
                code=result["code"])

        return result

    # ==========================================
    # Kakao AlimTalk Methods (PHP -> Python)
    # ==========================================

    async def cs_login_alert(
        self,
        phone: str,
        user_nick_name: str,
        counselor_code: str
    ) -> Dict[str, Any]:
        """상담사 접속 알림"""
        msg = f"#{{사주로 상담사 접속 알림 안내}}\n\n{user_nick_name} 선생님 현재 상담가능 합니다.\n\n접속 알림을 해둔 다른 고객님이 계시므로\n상담을 원하시면 서둘러주세요.\n*해당 알림은 1회성 알림으로\n다시 접속알림이 필요하신 분은 재설정 해주세요."
        pc_link = f"https://www.sajuline.com/counselor/{counselor_code}"
        mo_link = f"https://www.sajuline.com/counselor/{counselor_code}"
        template_id = "50047"

        return await self._create_and_send(
            recipient_type=RecipientType.USER,
            recipient_id="",
            phone=phone,
            template_id=template_id,
            msg_content=msg,
            pc_link=pc_link,
            mo_link=mo_link
        )

    async def cs_faq_alert(self, phone: str) -> Dict[str, Any]:
        """게시글 알림 (상담사)"""
        msg = "선생님에게 상담문의글이 작성되었습니다.\n확인하시어 답변or접속 부탁드립니다."
        pc_link = "https://sajutarot.com/app/cs/mypage"
        mo_link = "https://sajutarot.com/app/cs/mypage"
        template_id = "50046"

        return await self._create_and_send(
            recipient_type=RecipientType.COUNSELOR,
            recipient_id="",
            phone=phone,
            template_id=template_id,
            msg_content=msg,
            pc_link=pc_link,
            mo_link=mo_link
        )

    async def user_faq_alert(self, phone: str, user_nick_name: str) -> Dict[str, Any]:
        """게시글 알림 (고객)"""
        msg = f"{user_nick_name}님의 후기/문의글에 답변이 작성되었습니다.\n확인하시고 상담or접속알림 설정하시기 바랍니다."
        pc_link = "https://sajutarot.com/app/user/mypage"
        mo_link = "https://sajutarot.com/app/user/mypage"
        template_id = "50045"

        return await self._create_and_send(
            recipient_type=RecipientType.USER,
            recipient_id="",
            phone=phone,
            template_id=template_id,
            msg_content=msg,
            pc_link=pc_link,
            mo_link=mo_link
        )

    async def user_virtual_alert(
        self,
        phone: str,
        user_nick_name: str,
        regist_date: str,
        amount: int,
        order_no: str,
        product_name: str
    ) -> Dict[str, Any]:
        """무통장 입금 완료_수동"""
        site_nm = "사주타로"
        url = "https://sajutarot.com/app/user/history_charge"
        msg = f"{user_nick_name} 고객님의 입금 금액 확인되었습니다.\n\n결제일 : {regist_date}\n입금금액 : {amount}원\n주문번호 : {order_no}\n상품명 : {product_name}\n\n{site_nm} {url}"
        template_id = "50044"

        return await self._create_and_send(
            recipient_type=RecipientType.USER,
            recipient_id="",
            phone=phone,
            template_id=template_id,
            msg_content=msg,
            pc_link="",
            mo_link=""
        )

    async def user_money_request_alert(
        self,
        phone: str,
        user_nick_name: str,
        amount: int,
        bank: str,
        account: str,
        depositor: str,
        regist_date: str,
        product_name: str
    ) -> Dict[str, Any]:
        """입금 요청 수동"""
        msg = f"{user_nick_name} 고객님의 주문하신 상품이 미입금 상태입니다.\n해당 계좌로 미입금시 주문 자동취소됩니다.\n\n금액 : {amount}원\n입금계좌 : {bank} {account}\n예금주 : {depositor}\n주문일 : {regist_date}\n상품명 : {product_name}"
        template_id = "50043"

        return await self._create_and_send(
            recipient_type=RecipientType.USER,
            recipient_id="",
            phone=phone,
            template_id=template_id,
            msg_content=msg,
            pc_link="",
            mo_link=""
        )

    async def user_charge_confirm_alert(
        self,
        phone: str,
        user_nick_name: str,
        order_no: str,
        product_name: str,
        amount: int,
        point: int
    ) -> Dict[str, Any]:
        """결제 완료"""
        msg = f"{user_nick_name} 고객님의 소중한 주문 안내드립니다.\n주문번호 : {order_no}\n주문상품 : {product_name}\n금액 : {amount}원\n포인트 : {point}"
        template_id = "50042"
        pc_link = "https://www.sajuline.com/user/pointlog"
        mo_link = "https://www.sajuline.com/user/pointlog"

        return await self._create_and_send(
            recipient_type=RecipientType.USER,
            recipient_id="",
            phone=phone,
            template_id=template_id,
            msg_content=msg,
            pc_link=pc_link,
            mo_link=mo_link
        )

    async def user_join_alert(
        self,
        phone: str,
        nick_name: str,
        user_id: str
    ) -> Dict[str, Any]:
        """회원 가입 수동"""
        msg = f"{nick_name}님의 회원가입을 감사드립니다.\n즉시 사용가능한 10,000포인트가 지급되었습니다.\n\n해당 포인트는 추가결제 없이 사용가능한 포인트이며\n원하시는 선생님과 상담을 하실 수 있습니다.\n지급해드린 포인트가 모두 소진되면 자동으로 통화종료됩니다.\n아래 버튼을 클릭하시면 이용방법이 안내되어 있습니다.\n\n이 메시지는 고객님의 동의에 의해 지급된 회원가입 혜택 지급 메시지입니다."
        pc_link = "https://sajutarot.com/app/charge/guide"
        mo_link = "https://sajutarot.com/app/charge/guide"
        template_id = "50041"

        return await self._create_and_send(
            recipient_type=RecipientType.USER,
            recipient_id=user_id,
            phone=phone,
            template_id=template_id,
            msg_content=msg,
            pc_link=pc_link,
            mo_link=mo_link
        )
