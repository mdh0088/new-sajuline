import * as promiseAction from '@/api/_config/promiseAction';
import * as customerSupportApi from '@/api/customer-support/customer-supportApi';
import * as swal from '@/commonUtils/swal';
import {Reactive, Ref} from "vue";
import {UploadUserFile} from "element-plus";

export const getCsNoticeInfo = async (csNoticeInfo:Reactive<CsNoticeInfo>, attachFile:Ref<UploadUserFile[]>) => {

    console.log('chk csNoticeInfo.>',csNoticeInfo)
    //const uploadBaseUrl = 'https://sajuline.com/dev-upload/notice/';  // 경로를 변수로 설정
    const uploadBaseUrl = `${import.meta.env.VITE_APP_UPLOAD_URL}notice/`;

    const addFileToCollection = (key, value, targetArray) => {
        if (value) {  // 값이 존재하는지 확인
            targetArray.value.push({
                name: value,  // 파일 이름
                url: `${uploadBaseUrl}${value}`  // 파일 URL 경로 생성
            });
        }
    };

    let requests = [];
    requests.push(customerSupportApi.getCsNoticeInfo(csNoticeInfo.idx));
    const result = await promiseAction.promiseSettled(requests);

    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            // 매핑되지 않는 값 처리용 배열
            let unmappedKeys = Object.keys(value).filter(key => !(key in csNoticeInfo));


            Object.assign(csNoticeInfo, data.value);

            if (csNoticeInfo.attachFile != '') {
                addFileToCollection('img', csNoticeInfo.attachFile, attachFile);
            }

            console.log('csNoticeInfo.>',csNoticeInfo)
        }
    });
};

export const getCsNoticeList = async (queryParams:CustomerSupportRequest, tableOptions:Ref<TableOptions<CsNoticeInfo>>) => {
    let requests = [];
    tableOptions.value.isLoading = true;
    requests.push(customerSupportApi.getCsNoticeList(queryParams));
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
};

export const createCsNotice = async (csNoticeInfo, attachFile, doSearch) => {

    let requests = [];
    let formData = createFormData(attachFile.value);
    requests.push(customerSupportApi.createCsNotice(csNoticeInfo,formData));
    const result = await promiseAction.promiseSettled(requests);

    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            swal.swalAlert("생성 되었습니다.","success")
            doSearch();
        } else {
            swal.swalAlert(data.reason,"error")
        }
    });
};


export const modifyCsNotice = async (csNoticeInfo:Reactive<CsNoticeInfo>, attachFile:Ref<UploadUserFile[]>, doSearch) => {
    let requests = [];

    console.log('chk cs ifno >>',csNoticeInfo)
    let formData = createFormData(attachFile.value);
    requests.push(customerSupportApi.modifyCsNotice(csNoticeInfo,formData));
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
};


export const deleteCsNoticeInfo = async (csNoticeInfo:CsNoticeInfo) => {
    let requests = [];
    requests.push(customerSupportApi.deleteCsNoticeInfo(csNoticeInfo.idx));
    const result = await promiseAction.promiseSettled(requests);

    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            swal.swalAlert("삭제 되었습니다.","success")
        } else {
            swal.swalAlert(data.reason,"error")
        }
    });
};

const createFormData = (imgFileList) => {
    const formData = new FormData();
    imgFileList.forEach(file => {
        if (file.raw) {
            formData.append("imgUpload", file.raw);
        }
    });
    return formData;
}
