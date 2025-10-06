import { Ref } from 'vue';
import * as promiseAction from '@/api/_config/promiseAction';
import * as mileageProductApi from '@/api/mileage/mileageProductApi';
import * as swal from '@/commonUtils/swal';
import {createFormData} from "@/commonUtils/imgUtils";
import {UploadUserFile} from "element-plus";
import {MileageProductClass} from "@/models/mileage";

// 마일리지 상품 개별 조회
export const getMileageProductInfo = async (mileageProductInfo:Ref<MileageProductClass>, attachFile:Ref<UploadUserFile[]>) => {
    const uploadBaseUrl = `${import.meta.env.VITE_APP_UPLOAD_URL}mileage/`;
    const addFileToCollection = (key, value, fileNm, targetArray) => {
        if (value) {  // 값이 존재하는지 확인
            targetArray.value.push({
                name: fileNm,  // 파일 이름
                url: `${uploadBaseUrl}${value}`  // 파일 URL 경로 생성
            });
        }
    };


    let requests = [];
    requests.push(mileageProductApi.getMileageProduct(mileageProductInfo.value.m_product_idx));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            //console.log('chk data >>> ',data.value)
            //Object.assign(bannerInfo.value, data.value);
            mileageProductInfo.value.from(data.value);
            //bannerInfo.value = Banner.from(data.value)
            addFileToCollection('img', mileageProductInfo.value.m_product_img, mileageProductInfo.value.file_nm, attachFile);
        }
    });
}


// 마일리지 상품 목록 조회
export const getMileageProductList = async (tableOptions:Ref<TableOptions<MileageProductInfo>>) => {
    let requests = [];
    tableOptions.value.isLoading = true;
    const queryParams = {}
    requests.push(mileageProductApi.getMileageProductList(queryParams));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            tableOptions.value.items = value.items;
            tableOptions.value.isLoading = false;
        }
    });
}

// 마일리지 상품 생성
export const createMileageProduct= async (mileageProductInfo:Ref<MileageProductInfo>, attachFile, doSearch:Function) => {
    let requests = [];
    let formData = createFormData(attachFile.value);
    requests.push(mileageProductApi.createMileageProduct(mileageProductInfo.value, formData));
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


// 마일리지 상품 수정
export const updateMileageProduct= async (mileageProductInfo:Ref<MileageProductInfo>, attachFile, doSearch:Function) => {
    let requests = [];
    let formData = createFormData(attachFile.value);
    requests.push(mileageProductApi.updateMileageProduct(mileageProductInfo.value, formData));
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
