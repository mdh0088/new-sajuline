import { Ref } from 'vue';
import * as promiseAction from '@/api/_config/promiseAction';
import * as reviewApi from '@/api/review/reviewApi';
import * as swal from '@/commonUtils/swal';

export const getDumyReview = async (dumyReviewInfo:Ref<DumyReviewInfo>) => {
    let requests = [];
    requests.push(reviewApi.getDumyReview(dumyReviewInfo.value.idx));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            console.log('chk data >>> ',data.value)
            Object.assign(dumyReviewInfo.value, data.value);
        }
    });
}

export const getDumyReviewList = async (queryParams, tableOptions) => {
    let requests = [];
    tableOptions.value.isLoading = true;
    requests.push(reviewApi.getDumyReviewList(queryParams));
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

export const updateDumyReview= async (dumyReviewInfo:Ref<DumyReviewInfo>, doSearch:Function) => {
    let requests = [];
    requests.push(reviewApi.updateDumyReview(dumyReviewInfo.value));
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

export const deleteDumyReview = async (dumyReviewInfo) => {
    let requests = [];
    requests.push(reviewApi.deleteDumyReview(dumyReviewInfo.idx));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            console.log('chk data >>> ',data.value)
        }
    });
}


