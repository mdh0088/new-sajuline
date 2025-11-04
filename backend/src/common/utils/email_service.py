"""
이메일 전송 서비스 (Gmail SMTP)
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from src.config.settings import settings
from src.common.logging import get_logger_with_request_id
from src.exceptions.custom_exceptions import ValidationError


class EmailService:
    """Gmail SMTP 기반 이메일 전송 서비스"""

    def __init__(self):
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = settings.google_email_id
        self.sender_password = settings.google_email_password

        # 설정 검증
        if not self.sender_email or not self.sender_password:
            raise ValidationError("Gmail SMTP 설정이 누락되었습니다. GOOGLE_EMAIL_ID와 GOOGLE_EMAIL_PASSWORD를 확인하세요.")

    async def send_temporary_password(
        self,
        recipient_email: str,
        user_id: str,
        temporary_password: str
    ) -> bool:
        """
        임시 비밀번호 이메일 전송

        Args:
            recipient_email: 수신자 이메일
            user_id: 사용자 ID
            temporary_password: 임시 비밀번호 (평문)

        Returns:
            bool: 전송 성공 여부

        Raises:
            ValidationError: 이메일 전송 실패
        """
        log = get_logger_with_request_id()
        log.info("Sending temporary password email", recipient=recipient_email, user_id=user_id)

        try:
            # 이메일 메시지 생성
            message = MIMEMultipart("alternative")
            message["Subject"] = "[사주라인] 임시 비밀번호 안내"
            message["From"] = self.sender_email
            message["To"] = recipient_email

            # HTML 본문 생성
            html_body = self._create_temporary_password_html(user_id, temporary_password)

            # 텍스트 본문 생성 (HTML 미지원 클라이언트용)
            text_body = self._create_temporary_password_text(user_id, temporary_password)

            # 메시지에 본문 추가
            part1 = MIMEText(text_body, "plain", "utf-8")
            part2 = MIMEText(html_body, "html", "utf-8")
            message.attach(part1)
            message.attach(part2)

            # SMTP 연결 및 전송
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.sender_email,
                password=self.sender_password,
            )

            log.info("Temporary password email sent successfully", recipient=recipient_email)
            return True

        except aiosmtplib.SMTPException as e:
            log.error(
                "SMTP error while sending email",
                recipient=recipient_email,
                error=str(e),
                error_type=type(e).__name__,
                smtp_host=self.smtp_host,
                smtp_port=self.smtp_port,
                sender_email=self.sender_email
            )
            raise ValidationError(
                f"이메일 전송 실패: {str(e)}\n"
                f"SMTP 설정을 확인하세요. Gmail의 경우 '앱 비밀번호'가 필요합니다."
            )
        except Exception as e:
            log.error("Unexpected error while sending email", recipient=recipient_email, error=str(e))
            raise ValidationError(f"이메일 전송 중 예기치 않은 오류가 발생했습니다: {str(e)}")

    def _create_temporary_password_text(self, user_id: str, temporary_password: str) -> str:
        """텍스트 이메일 본문 생성"""
        return f"""
사주라인 임시 비밀번호 안내

안녕하세요, {user_id}님.

요청하신 임시 비밀번호를 안내드립니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━
임시 비밀번호: {temporary_password}
━━━━━━━━━━━━━━━━━━━━━━━━━━

보안을 위해 로그인 후 반드시 비밀번호를 변경해주세요.

※ 본 메일은 발신전용이므로 회신되지 않습니다.

감사합니다.
사주라인 드림
        """.strip()

    def _create_temporary_password_html(self, user_id: str, temporary_password: str) -> str:
        """HTML 이메일 본문 생성"""
        return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>사주라인 임시 비밀번호</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- 헤더 -->
                    <tr>
                        <td style="padding: 40px 40px 20px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">🔐 임시 비밀번호 안내</h1>
                        </td>
                    </tr>

                    <!-- 본문 -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 20px; color: #333333; font-size: 16px; line-height: 1.6;">
                                안녕하세요, <strong>{user_id}</strong>님.
                            </p>

                            <p style="margin: 0 0 30px; color: #666666; font-size: 15px; line-height: 1.6;">
                                요청하신 임시 비밀번호를 안내드립니다.
                            </p>

                            <!-- 임시 비밀번호 박스 -->
                            <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); border: 2px solid #667eea; border-radius: 8px; padding: 24px; margin: 0 0 30px; text-align: center;">
                                <p style="margin: 0 0 12px; color: #667eea; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                                    임시 비밀번호
                                </p>
                                <p style="margin: 0; color: #333333; font-size: 28px; font-weight: bold; font-family: 'Courier New', monospace; letter-spacing: 2px;">
                                    {temporary_password}
                                </p>
                            </div>

                            <!-- 안내 사항 -->
                            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 16px; margin: 0 0 30px; border-radius: 4px;">
                                <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.6;">
                                    ⚠️ <strong>보안 안내</strong><br>
                                    로그인 후 반드시 비밀번호를 변경해주세요.
                                </p>
                            </div>

                            <p style="margin: 0 0 10px; color: #999999; font-size: 13px; line-height: 1.6;">
                                본인이 요청하지 않은 경우, 즉시 고객센터로 문의해주세요.
                            </p>

                            <p style="margin: 0; color: #999999; font-size: 13px; line-height: 1.6;">
                                ※ 본 메일은 발신전용이므로 회신되지 않습니다.
                            </p>
                        </td>
                    </tr>

                    <!-- 푸터 -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f9fa; border-radius: 0 0 12px 12px; text-align: center;">
                            <p style="margin: 0; color: #6c757d; font-size: 14px;">
                                감사합니다.<br>
                                <strong style="color: #667eea;">사주라인</strong> 드림
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """.strip()

    def mask_email(self, email: str) -> str:
        """
        이메일 주소 마스킹
        예: test@example.com -> t***@example.com
        """
        if "@" not in email:
            return email

        local, domain = email.split("@", 1)

        if len(local) <= 1:
            masked_local = local
        elif len(local) <= 3:
            masked_local = local[0] + "*" * (len(local) - 1)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"


# 싱글톤 인스턴스
email_service = EmailService()
