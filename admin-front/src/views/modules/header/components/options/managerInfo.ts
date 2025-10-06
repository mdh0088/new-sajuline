import * as promiseAction from '@/api/_config/promiseAction';
import * as managerApi from '@/api/manager/managerApi';
import * as swal from '@/commonUtils/swal';
import { useUserStore } from '@/store/user';

export const modifyMnager = async (managerInfo) => {
    const userStore = useUserStore();
    let requests = [];
    requests.push(managerApi.modifyMnager(managerInfo.value));
    const result = await promiseAction.promiseSettled(requests);
    result.forEach(data => {
        const { success, value } = data;
        if (success) {

            userStore.setLogin(value);
            swal.swalAlert("수정 되었습니다.", 'success');
        } else {
            console.log('chk result >>>',data)
            swal.swalAlert(data.reason, 'error');
        }
    });
};