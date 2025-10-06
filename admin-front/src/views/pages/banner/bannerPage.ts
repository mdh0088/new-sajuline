import { Ref } from 'vue';
import * as promiseAction from '@/api/_config/promiseAction';
import * as bannerApi from '@/api/banner/bannerApi';
import * as swal from '@/commonUtils/swal';
import {createFormData} from "@/commonUtils/imgUtils";
import {BannerClass} from "@/models/banner";
import {UploadUserFile} from "element-plus";

// 배너 개별 조회
export const getBannerInfo = async (bannerInfo:Ref<BannerClass>, attachFile:Ref<UploadUserFile[]>) => {
    //const uploadBaseUrl = 'https://sajuline.com/dev-upload/banner/';  // 경로를 변수로 설정
    const uploadBaseUrl = `${import.meta.env.VITE_APP_UPLOAD_URL}banner/`;

    const addFileToCollection = (key, value, fileNm, targetArray) => {
        if (value) {  // 값이 존재하는지 확인
            targetArray.value.push({
                name: fileNm,  // 파일 이름
                url: `${uploadBaseUrl}${value}`  // 파일 URL 경로 생성
            });
        }
    };


    let requests = [];
    requests.push(bannerApi.getBanner(bannerInfo.value.banner_idx));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            //console.log('chk data >>> ',data.value)
            //Object.assign(bannerInfo.value, data.value);
            bannerInfo.value.from(data.value);
            //bannerInfo.value = Banner.from(data.value)
            addFileToCollection('img', bannerInfo.value.bannerImg, bannerInfo.value.fileNm, attachFile);
        }
    });
}

// 배너 목록 조회
export const getBannerList = async (queryParams:BannerRequest, tableOptions:Ref<TableOptions<BannerInfo>>) => {
    let requests = [];
    tableOptions.value.isLoading = true;
    requests.push(bannerApi.getBannerList(queryParams));
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
export const createBanner= async (bannerInfo:Ref<BannerInfo>, attachFile, doSearch:Function) => {
    let requests = [];
    let formData = createFormData(attachFile.value);
    requests.push(bannerApi.createBanner(bannerInfo.value, formData));
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
export const updateBanner= async (bannerInfo:Ref<BannerInfo>, attachFile, doSearch:Function) => {
    let requests = [];
    let formData = createFormData(attachFile.value);
    requests.push(bannerApi.updateBanner(bannerInfo.value, formData));
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
export const deleteBanner = async (bannerInfo:BannerInfo) => {
    let requests = [];
    requests.push(bannerApi.deleteBanner(bannerInfo.banner_idx));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            console.log('chk data >>> ',data.value)
        }
    });
}

export const getBannerOrderNo = async (bannerOrdList:Ref<Array<BannerInfo>>) => {
    let requests = [];

    requests.push(bannerApi.getBannerOrderNo());
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            bannerOrdList.value = BannerClass.fromArray(data.value)
        }
    });
}
