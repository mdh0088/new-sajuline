

const showLoading = () => {
    document.querySelector("#loading-overlay").classList.remove("hidden");
    document.querySelector("#loading-overlay").style.display = "block";
}

const hideLoading = () => {
    document.getElementById("loading-overlay").classList.add("hidden");
    document.querySelector("#loading-overlay").style.display = "none";
}

//return true
const isMobile = () => {
    return /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
}

/*
function validatePhoneNumber(phoneNumber) {
    var strippedNumber = phoneNumber.replace(/-/g, ''); // remove all '-' symbols
    var pattern = /^01[0|1|6|7|8|9][0-9]{7,8}$/; // Korean phone number format
    return pattern.test(strippedNumber);
}
*/

function validatePhoneNumber(phoneNumber) {
    var strippedNumber = phoneNumber.replace(/[-\s\(\)]/g, ''); // remove all '-', ' ', '(', and ')' symbols
    var pattern = /^01[0|1|6|7|8|9][0-9]{7,8}$/; // Korean phone number format
    return pattern.test(strippedNumber);
}

//null체크
function isNull(value) {
    return (value === null || value === undefined || value.trim() === '');
}

//이메일 체크
function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

//숫자, 영문만
function validateInputId(input) {
    var regex = /^[a-zA-Z0-9]+$/;
    return regex.test(input);
}

//한글 2자 이상 영문 4글자 이상 확인
function validateInputNickName(input) {
    var koreanRegex = /^[가-힣]{2,}$/;
    var englishRegex = /^[a-zA-Z]{4,}$/;
    return koreanRegex.test(input) || englishRegex.test(input);
}

//비번체크
function isValidPassword(password) {
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
    return passwordRegex.test(password);
}
