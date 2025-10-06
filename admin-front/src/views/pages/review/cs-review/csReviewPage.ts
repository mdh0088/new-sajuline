import { Ref } from 'vue';
import * as promiseAction from '@/api/_config/promiseAction';
import * as reviewApi from '@/api/review/reviewApi';
import * as swal from '@/commonUtils/swal';

export const getCsReviewInfo = async (csReviewInfo:Ref<CsReviewInfo>) => {
    let requests = [];
    requests.push(reviewApi.getCsReview(csReviewInfo.value.idx));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            console.log('chk data >>> ',data.value)
            Object.assign(csReviewInfo.value, data.value);
        }
    });
}

export const getCsReviewList = async (queryParams, tableOptions) => {
    let requests = [];
    tableOptions.value.isLoading = true;
    requests.push(reviewApi.getCsReviewList(queryParams));
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

export const updateCsReview= async (csReviewInfo:Ref<CsReviewInfo>, doSearch:Function) => {
    let requests = [];
    requests.push(reviewApi.updateCsReview(csReviewInfo.value));
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

export const deleteCsReview = async (csReviewInfo) => {
    let requests = [];
    requests.push(reviewApi.deleteCsReview(csReviewInfo.idx));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            console.log('chk data >>> ',data.value)
        }
    });
}



