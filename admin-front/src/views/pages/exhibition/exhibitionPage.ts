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
            exhibitionInfo.value.from(data.value)
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
            tableOptions.value.items = value.items;
            tableOptions.value.totalCnt = value.total_count;
            tableOptions.value.isLoading = false;
        }
    });
}

// 기획전 생성
export const createExhibition= async (exhibitionInfo:Ref<ExhibitionInfo>, attachFile, doSearch:Function) => {
    let requests = [];
    let formData = createFormData(attachFile.value);
    requests.push(exhibitionApi.createExhibition(exhibitionInfo.value, formData));
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
    requests.push(exhibitionApi.updateExhibition(exhibitionInfo.value, formData));
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

