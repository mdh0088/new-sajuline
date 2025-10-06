import Swal from 'sweetalert2';
import {ref} from "vue";

// type : success, error, warning, info, question

const confirmButtonColor = ref('#0072F8');

export function swalAlert(message, type) {
    // const number = Number.parseInt(num);
    Swal.fire({
        text: message,
        icon: type,
        confirmButtonText: '확인',
        confirmButtonColor: confirmButtonColor.value
    });
}

export function swalConfirm(message, type) {
    return Swal.fire({
        title: message,
        icon: type,
        showCancelButton: true,
        confirmButtonText: '예',
        confirmButtonColor: confirmButtonColor.value,
        cancelButtonText: '아니오',
        cancelButtonColor: '#7366FF0F'
    });
}

export function swalConfirmWithContent(message, type) {
    return Swal.fire({
        text: message,
        icon: type,
        showCancelButton: true,
        confirmButtonText: '예',
        confirmButtonColor: confirmButtonColor.value,
        cancelButtonText: '아니오',
        cancelButtonColor: '#7366FF0F'
    });
}

export function swalConfirmWithHtml(message, type) {
    return Swal.fire({
        html: message,
        icon: type,
        showCancelButton: true,
        confirmButtonText: '예',
        confirmButtonColor: confirmButtonColor.value,
        cancelButtonText: '아니오',
        cancelButtonColor: '#7366FF0F'
    });
}

export function swalConfirmWithHtmlNoCancel(message, type) {
    return Swal.fire({
        html: message,
        icon: type,
        confirmButtonText: '확인',
        confirmButtonColor: confirmButtonColor.value,
    });
}

export function swalConfirmWithNoCancel(message, type) {
    return Swal.fire({
        title: message,
        icon: type,
        confirmButtonText: '확인',
        confirmButtonColor: confirmButtonColor.value
    });
}

export function swalToast(message, type) {
    return Swal.fire({
        toast: true,
        // icon: type,
        animation: false,
        title: message,
        position: 'bottom',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: false
    });
}
