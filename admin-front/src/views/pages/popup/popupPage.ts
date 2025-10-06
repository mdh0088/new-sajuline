import { Ref } from 'vue';
import * as promiseAction from '@/api/_config/promiseAction';
import * as popupApi from '@/api/popup/popupApi';
import * as swal from '@/commonUtils/swal';
import {UploadUserFile} from "element-plus";
import {PopupClass} from "@/models/popup"
import {createFormData} from "@/commonUtils/imgUtils";
import * as bannerApi from "@/api/banner/bannerApi";
import {BannerClass} from "@/models/banner";

// 배너 개별 조회
export const getPopupInfo = async (popupInfo:Ref<PopupClass>, attachFile:Ref<UploadUserFile[]>) => {
    //const uploadBaseUrl = 'https://sajuline.com/dev-upload/popup/';  // 경로를 변수로 설정
    const uploadBaseUrl = `${import.meta.env.VITE_APP_UPLOAD_URL}popup/`;
    const addFileToCollection = (key, value, fileNm, targetArray) => {
        if (value) {  // 값이 존재하는지 확인
            targetArray.value.push({
                name: fileNm,  // 파일 이름
                url: `${uploadBaseUrl}${value}`  // 파일 URL 경로 생성
            });
        }
    };

    let requests = [];
    requests.push(popupApi.getPopup(popupInfo.value.popup_idx));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            popupInfo.value.from(data.value);
            addFileToCollection('img', popupInfo.value.popupImg, popupInfo.value.fileNm, attachFile);
        }
    });
}

// 배너 목록 조회
export const getPopupList = async (queryParams:PopupRequest, tableOptions:Ref<TableOptions<PopupInfo>>) => {
    let requests = [];
    tableOptions.value.isLoading = true;
    requests.push(popupApi.getPopupList(queryParams));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            console.log('chk data >>> ',data.value)
            tableOptions.value.items = value.items;
            tableOptions.value.totalCnt = value.total_count;
            tableOptions.value.isLoading = false;
        }
    });
}

// 배너 생성
export const createPopup= async (popupInfo:Ref<PopupInfo>, attachFile, doSearch:Function) => {
    let requests = [];
    let formData = createFormData(attachFile.value);
    requests.push(popupApi.createPopup(popupInfo.value, formData));
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

// 배너 수정
export const updatePopup= async (popupInfo:Ref<PopupInfo>, attachFile, doSearch:Function) => {
    let requests = [];
    let formData = createFormData(attachFile.value);
    requests.push(popupApi.updatePopup(popupInfo.value,formData));
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

// 배너 삭제
export const deletePopup = async (popupInfo:PopupInfo) => {
    let requests = [];
    requests.push(popupApi.deletePopup(popupInfo.popup_idx));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            console.log('chk data >>> ',data.value)
        }
    });
}


export const getPopupOrderNo = async (popupOrdList:Ref<Array<PopupInfo>>) => {
    let requests = [];

    requests.push(popupApi.getPopupOrderNo());
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            popupOrdList.value = PopupClass.fromArray(data.value)
        }
    });
}
