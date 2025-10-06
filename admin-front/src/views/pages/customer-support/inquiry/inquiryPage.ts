import * as promiseAction from '@/api/_config/promiseAction';
import * as customerSupportApi from '@/api/customer-support/customer-supportApi';
import * as swal from '@/commonUtils/swal';


export const getCsAdminFaqInfo = async (csAdminFaqInfo) => {

    let requests = [];
    requests.push(customerSupportApi.getCsAdminFaq(csAdminFaqInfo.idx));
    const result = await promiseAction.promiseSettled(requests);

    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            Object.assign(csAdminFaqInfo, data.value);
        }
    });
};

export const getCsAdminFaqList = async (queryParams, tableOptions) => {
    let requests = [];
    tableOptions.value.isLoading = true;
    requests.push(customerSupportApi.getCsAdminFaqList(queryParams));
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

export const modifyCsAdminFaq = async (csAdminFaqInfo, doSearch) => {
    let requests = [];
    requests.push(customerSupportApi.modifyCsAdminFaq(csAdminFaqInfo));
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



export const deleteCsAdminFaq = async (csAdminFaqInfo) => {
    let requests = [];
    requests.push(customerSupportApi.deleteCsAdminFaq(csAdminFaqInfo.idx));
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



export const getAdminFaq = async (adminFaqInfo) => {

    let requests = [];
    requests.push(customerSupportApi.getAdminFaq(adminFaqInfo.idx));
    const result = await promiseAction.promiseSettled(requests);

    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            Object.assign(adminFaqInfo, data.value);
        }
    });
};

export const getAdminFaqList = async (queryParams, tableOptions) => {
    let requests = [];
    tableOptions.value.isLoading = true;
    requests.push(customerSupportApi.getAdminFaqList(queryParams));
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

export const modifyAdminFaq = async (adminFaqInfo, doSearch) => {
    let requests = [];
    requests.push(customerSupportApi.modifyAdminFaq(adminFaqInfo));
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



export const deleteAdminFaq = async (adminFaqInfo) => {
    let requests = [];
    requests.push(customerSupportApi.deleteAdminFaq(adminFaqInfo.idx));
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



export const getCsFaq = async (csFaqInfo) => {

    let requests = [];
    requests.push(customerSupportApi.getCsFaq(csFaqInfo.idx));
    const result = await promiseAction.promiseSettled(requests);

    result.forEach(data => {
        const { success, value } = data;
        if (success) {
            Object.assign(csFaqInfo, data.value);
        }
    });
};

export const getCsFaqList = async (queryParams, tableOptions) => {
    let requests = [];
    tableOptions.value.isLoading = true;
    requests.push(customerSupportApi.getCsFaqList(queryParams));
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

export const modifyCsFaq = async (csFaqInfo, doSearch) => {
    let requests = [];
    requests.push(customerSupportApi.modifyCsFaq(csFaqInfo));
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



export const deleteCsFaq = async (csFaqInfo) => {
    let requests = [];
    requests.push(customerSupportApi.deleteCsFaq(csFaqInfo.idx));
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