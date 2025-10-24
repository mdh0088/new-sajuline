import { Ref } from 'vue';
import * as promiseAction from '@/api/_config/promiseAction';
import * as exhibitionApi from '@/api/exhibition/exhibitionApi';
import * as swal from '@/commonUtils/swal';
import {UploadUserFile} from "element-plus";
import {ExhibitionClass} from "@/models/exhibition";
import {createFormData} from "@/commonUtils/imgUtils";

// 기획전 개별 조회
export const getExhibitionInfo = async ( exhibitionInfo:Ref<ExhibitionClass>, attachFile:Ref<UploadUserFile[]>) => {
    //const uploadBaseUrl = 'https://sajuline.com/dev-upload/exhibition/';  // 경로를 변수로 설정
    const uploadBaseUrl = `${import.meta.env.VITE_APP_UPLOAD_URL}exhibition/`;


    const addFileToCollection = (key, value, fileNm, targetArray) => {
        if (value) {  // 값이 존재하는지 확인
            targetArray.value.push({
                name: fileNm,  // 파일 이름
                url: `${uploadBaseUrl}${value}`  // 파일 URL 경로 생성
            });
        }
    };

    let requests = [];
    requests.push(exhibitionApi.getExhibition(exhibitionInfo.value.exhibition_idx));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            console.log('chk data >>> ',data.value)

            // 백엔드 응답을 프론트엔드 형식으로 매핑
            const apiData = value.data;
            const mappedData = {
                exhibition_idx: apiData.event_id,
                exhibitionNm: apiData.event_name,
                bannerImg: apiData.banner_image_url || '',
                fileNm: apiData.banner_image_url ? apiData.banner_image_url.split('/').pop() : '',
                startDate: apiData.valid_from,
                endDate: apiData.valid_until,
                showYn: apiData.is_active ? 'Y' : 'N',
                registDate: apiData.created_at,
                updateDate: apiData.updated_at,
                // 추가 필드
                event_code: apiData.event_code,
                event_type: apiData.event_type,
                description: apiData.description,
                terms: apiData.terms,
                reward_type: apiData.reward_type,
                reward_value: apiData.reward_value,
                max_participants: apiData.max_participants,
                current_participants: apiData.current_participants,
                metadata_json: apiData.metadata_json,
                replayList: [] // 댓글은 별도 API로 조회해야 함
            };

            exhibitionInfo.value.from(mappedData);
            addFileToCollection('img', exhibitionInfo.value.bannerImg, exhibitionInfo.value.fileNm, attachFile);
        }
    });
}

// 기획전 목록 조회
export const getExhibitionList = async (queryParams:ExhibitionRequest, tableOptions:Ref<TableOptions<ExhibitionInfo>>) => {
    let requests = [];
    tableOptions.value.isLoading = true;
    requests.push(exhibitionApi.getExhibitionList(queryParams));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            console.log('chk data >>> ',data.value)
            // 백엔드 응답을 프론트엔드 형식으로 매핑
            const mappedItems = value.data.items.map((item: any) => ({
                exhibition_idx: item.event_id,
                exhibitionNm: item.event_name,
                fileNm: item.banner_image_url || '',
                bannerImg: item.banner_image_url || '',
                startDate: item.valid_from,
                endDate: item.valid_until,
                showYn: item.is_active ? 'Y' : 'N',
                registDate: item.created_at,
                updateDate: item.updated_at,
                // 추가 필드
                event_code: item.event_code,
                event_type: item.event_type,
                description: item.description,
                terms: item.terms,
                reward_type: item.reward_type,
                reward_value: item.reward_value,
                max_participants: item.max_participants,
                current_participants: item.current_participants,
                metadata_json: item.metadata_json
            }));

            tableOptions.value.items = mappedItems;
            tableOptions.value.totalCnt = value.data.total;
            tableOptions.value.isLoading = false;
        }
    });
}

// 기획전 생성
export const createExhibition= async (exhibitionInfo:Ref<ExhibitionInfo>, attachFile, doSearch:Function) => {
    let requests = [];
    let formData = createFormData(attachFile.value);

    // 날짜를 문자열로 변환하는 함수
    const formatDateTime = (date: any): string | null => {
        if (!date) return null;
        if (typeof date === 'string') return date;
        if (date instanceof Date) {
            // YYYY-MM-DD HH:mm:ss 형식으로 변환
            const pad = (n: number) => n.toString().padStart(2, '0');
            return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
        }
        return null;
    };

    // 프론트엔드 형식을 백엔드 형식으로 변환
    const backendData = {
        event_name: exhibitionInfo.value.exhibitionNm,
        event_type: (exhibitionInfo.value as any).event_type || 'POINT',
        description: (exhibitionInfo.value as any).description || '',
        terms: (exhibitionInfo.value as any).terms || null,
        reward_type: (exhibitionInfo.value as any).reward_type || 'POINT',
        reward_value: (exhibitionInfo.value as any).reward_value || 0,
        max_participants: (exhibitionInfo.value as any).max_participants || null,
        is_active: exhibitionInfo.value.showYn === 'Y',
        valid_from: formatDateTime(exhibitionInfo.value.startDate),
        valid_until: formatDateTime(exhibitionInfo.value.endDate),
        banner_image_url: exhibitionInfo.value.bannerImg || null,
        metadata: (exhibitionInfo.value as any).metadata_json || null
    };

    requests.push(exhibitionApi.createExhibition(backendData, formData));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            swal.swalAlert("저장 되었습니다.","success")
            doSearch();
        } else {
            swal.swalAlert(data.reason,"error")
        }
    });
}

// 기획전 수정
export const updateExhibition= async (exhibitionInfo:Ref<ExhibitionInfo>, attachFile, doSearch:Function) => {
    let requests = [];
    let formData = createFormData(attachFile.value);

    // 날짜를 문자열로 변환하는 함수
    const formatDateTime = (date: any): string | null => {
        if (!date) return null;
        if (typeof date === 'string') return date;
        if (date instanceof Date) {
            // YYYY-MM-DD HH:mm:ss 형식으로 변환
            const pad = (n: number) => n.toString().padStart(2, '0');
            return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
        }
        return null;
    };

    // 프론트엔드 형식을 백엔드 형식으로 변환
    const backendData = {
        event_id: exhibitionInfo.value.exhibition_idx,
        event_name: exhibitionInfo.value.exhibitionNm,
        event_type: (exhibitionInfo.value as any).event_type || 'POINT',
        description: (exhibitionInfo.value as any).description || '',
        terms: (exhibitionInfo.value as any).terms || null,
        reward_type: (exhibitionInfo.value as any).reward_type || 'POINT',
        reward_value: (exhibitionInfo.value as any).reward_value || 0,
        max_participants: (exhibitionInfo.value as any).max_participants || null,
        is_active: exhibitionInfo.value.showYn === 'Y',
        valid_from: formatDateTime(exhibitionInfo.value.startDate),
        valid_until: formatDateTime(exhibitionInfo.value.endDate),
        banner_image_url: exhibitionInfo.value.bannerImg || null,
        metadata: (exhibitionInfo.value as any).metadata_json || null
    };

    console.log('Sending data to backend:', backendData);
    console.log('startDate:', exhibitionInfo.value.startDate, 'type:', typeof exhibitionInfo.value.startDate);
    console.log('endDate:', exhibitionInfo.value.endDate, 'type:', typeof exhibitionInfo.value.endDate);

    requests.push(exhibitionApi.updateExhibition(backendData, formData));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            swal.swalAlert("저장 되었습니다.","success")
            doSearch();
        } else {
            swal.swalAlert(data.reason,"error")
        }
    });
}

// 기획전 삭제
export const deleteExhibition = async (exhibitionInfo:ExhibitionInfo) => {
    let requests = [];
    requests.push(exhibitionApi.deleteExhibition(exhibitionInfo.exhibition_idx));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            swal.swalAlert("저장 되었습니다.","success")
        } else {
            swal.swalAlert(data.reason,"error")
        }
    });
}

// 기획전 삭제
export const deleteExhibitionReply = async (exhibitionReplyInfo:ExhibitionReplyInfo, exhibitionInfo:Ref<ExhibitionInfo>) => {
    let requests = [];
    requests.push(exhibitionApi.deleteExhibitionReply(exhibitionReplyInfo.reply_idx));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            swal.swalAlert("저장 되었습니다.","success")
            if (exhibitionInfo.value && exhibitionInfo.value.replayList) {
                const index = exhibitionInfo.value.replayList.findIndex(
                    item => item.reply_idx === exhibitionReplyInfo.reply_idx
                );

                // 해당 인덱스가 존재하면 삭제
                if (index !== -1) {
                    exhibitionInfo.value.replayList.splice(index, 1);
                }
            }
        } else {
            swal.swalAlert(data.reason,"error")
        }
    });
}

