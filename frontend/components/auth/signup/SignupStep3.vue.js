"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
var useValidation_1 = require("~/composables/validation/useValidation");
// defineModel로 간단하게 처리
var signupFormData = defineModel('signupFormData', { required: true });
// Step3 자체 검증 로직
var validateBirthDate = (0, useValidation_1.useValidation)().validateBirthDate;
// Element Plus DatePicker를 위한 로컬 상태
var birthDate = ref('');
var birthTime = ref('');
// birth_date 통합 처리 함수
var updateBirthDate = function () {
    if (birthDate.value) {
        // 날짜만 있는 경우: YYYY-MM-DD 00:00
        var dateTimeString = "".concat(birthDate.value, " 00:00");
        // 시간도 있는 경우: YYYY-MM-DD HH:MM
        if (birthTime.value) {
            dateTimeString = "".concat(birthDate.value, " ").concat(birthTime.value);
        }
        signupFormData.value.birth_date = dateTimeString;
    }
    else {
        signupFormData.value.birth_date = '';
    }
};
// 초기값 설정 (기존 birth_date에서 날짜/시간 분리)
onMounted(function () {
    var existingBirthDate = signupFormData.value.birth_date;
    if (existingBirthDate) {
        var parts = existingBirthDate.split(' ');
        if (parts.length >= 1 && parts[0]) {
            birthDate.value = parts[0]; // YYYY-MM-DD 부분
        }
        if (parts.length >= 2 && parts[1] && parts[1] !== '00:00') {
            birthTime.value = parts[1]; // HH:MM 부분 (00:00이 아닌 경우에만)
        }
    }
});
// 날짜 선택 핸들러
var handleBirthDateChange = function (value) {
    birthDate.value = value || '';
    updateBirthDate();
};
// 시간 선택 핸들러
var handleBirthTimeChange = function (value) {
    birthTime.value = value || '';
    updateBirthDate();
};
// 날짜 비활성화 함수 (1900년 이전, 미래 날짜 비활성화)
var disabledDate = function (time) {
    var currentDate = new Date();
    var minDate = new Date('1900-01-01');
    return time.getTime() > currentDate.getTime() || time.getTime() < minDate.getTime();
};
// 생년월일 유효성 검증
var birthValidator = computed(function () {
    var birthDateValue = signupFormData.value.birth_date;
    // 필수 필드 체크
    if (!birthDateValue || !birthDate.value) {
        return {
            isValid: false,
            message: '생년월일을 선택해주세요.'
        };
    }
    // 날짜 유효성 검증 (날짜 부분만 검증)
    return validateBirthDate(birthDate.value);
});
// Step3 종합 검증 결과
var validator = computed(function () { return ({
    birthValidator: birthValidator,
    isValid: birthValidator.value.isValid
}); });
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_defaults = {};
var __VLS_modelEmit = defineEmits();
var __VLS_ctx = {};
var __VLS_elements;
var __VLS_components;
var __VLS_directives;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "form-section" }));
__VLS_asFunctionalElement(__VLS_elements.h2, __VLS_elements.h2)(__assign({ class: "section-title" }));
__VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "section-subtitle" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-group" }));
__VLS_asFunctionalElement(__VLS_elements.label, __VLS_elements.label)(__assign({ class: "input-label" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "date-picker-container" }));
var __VLS_0 = {}.ElDatePicker;
/** @type {[typeof __VLS_components.ElDatePicker, typeof __VLS_components.elDatePicker, ]} */ ;
// @ts-ignore
ElDatePicker;
// @ts-ignore
var __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0(__assign(__assign(__assign({ 'onChange': {} }, { modelValue: (__VLS_ctx.birthDate), type: "date", placeholder: "생년월일을 선택해주세요", format: "YYYY-MM-DD", valueFormat: "YYYY-MM-DD", disabledDate: (__VLS_ctx.disabledDate), clearable: (false) }), { class: "birth-date-picker custom-date-input" }), { size: "large" })));
var __VLS_2 = __VLS_1.apply(void 0, __spreadArray([__assign(__assign(__assign({ 'onChange': {} }, { modelValue: (__VLS_ctx.birthDate), type: "date", placeholder: "생년월일을 선택해주세요", format: "YYYY-MM-DD", valueFormat: "YYYY-MM-DD", disabledDate: (__VLS_ctx.disabledDate), clearable: (false) }), { class: "birth-date-picker custom-date-input" }), { size: "large" })], __VLS_functionalComponentArgsRest(__VLS_1), false));
var __VLS_4;
var __VLS_5;
var __VLS_6 = ({ change: {} },
    { onChange: (__VLS_ctx.handleBirthDateChange) });
// @ts-ignore
[birthDate, disabledDate, handleBirthDateChange,];
var __VLS_3;
if (__VLS_ctx.validator.birthValidator.value.message) {
    // @ts-ignore
    [validator,];
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "validation-text" }, { class: ({
            'error-text': !__VLS_ctx.validator.birthValidator.value.isValid,
            'success-text': __VLS_ctx.validator.birthValidator.value.isValid && __VLS_ctx.birthDate
        }) }));
    // @ts-ignore
    [birthDate, validator, validator,];
    (__VLS_ctx.validator.birthValidator.value.message);
    // @ts-ignore
    [validator,];
}
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-group" }));
__VLS_asFunctionalElement(__VLS_elements.label, __VLS_elements.label)(__assign({ class: "input-label" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "time-input-container" }));
var __VLS_8 = {}.ElTimePicker;
/** @type {[typeof __VLS_components.ElTimePicker, typeof __VLS_components.elTimePicker, ]} */ ;
// @ts-ignore
ElTimePicker;
// @ts-ignore
var __VLS_9 = __VLS_asFunctionalComponent(__VLS_8, new __VLS_8(__assign(__assign(__assign({ 'onChange': {} }, { modelValue: (__VLS_ctx.birthTime), placeholder: "태어난 시간을 선택해주세요", format: "HH:mm", valueFormat: "HH:mm" }), { class: "birth-time-picker custom-date-input" }), { size: "large" })));
var __VLS_10 = __VLS_9.apply(void 0, __spreadArray([__assign(__assign(__assign({ 'onChange': {} }, { modelValue: (__VLS_ctx.birthTime), placeholder: "태어난 시간을 선택해주세요", format: "HH:mm", valueFormat: "HH:mm" }), { class: "birth-time-picker custom-date-input" }), { size: "large" })], __VLS_functionalComponentArgsRest(__VLS_9), false));
var __VLS_12;
var __VLS_13;
var __VLS_14 = ({ change: {} },
    { onChange: (__VLS_ctx.handleBirthTimeChange) });
// @ts-ignore
[birthTime, handleBirthTimeChange,];
var __VLS_11;
__VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "help-text" }));
/** @type {__VLS_StyleScopedClasses['form-section']} */ ;
/** @type {__VLS_StyleScopedClasses['section-title']} */ ;
/** @type {__VLS_StyleScopedClasses['section-subtitle']} */ ;
/** @type {__VLS_StyleScopedClasses['input-group']} */ ;
/** @type {__VLS_StyleScopedClasses['input-label']} */ ;
/** @type {__VLS_StyleScopedClasses['date-picker-container']} */ ;
/** @type {__VLS_StyleScopedClasses['birth-date-picker']} */ ;
/** @type {__VLS_StyleScopedClasses['custom-date-input']} */ ;
/** @type {__VLS_StyleScopedClasses['validation-text']} */ ;
/** @type {__VLS_StyleScopedClasses['error-text']} */ ;
/** @type {__VLS_StyleScopedClasses['success-text']} */ ;
/** @type {__VLS_StyleScopedClasses['input-group']} */ ;
/** @type {__VLS_StyleScopedClasses['input-label']} */ ;
/** @type {__VLS_StyleScopedClasses['time-input-container']} */ ;
/** @type {__VLS_StyleScopedClasses['birth-time-picker']} */ ;
/** @type {__VLS_StyleScopedClasses['custom-date-input']} */ ;
/** @type {__VLS_StyleScopedClasses['help-text']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () { return ({
        birthDate: birthDate,
        birthTime: birthTime,
        handleBirthDateChange: handleBirthDateChange,
        handleBirthTimeChange: handleBirthTimeChange,
        disabledDate: disabledDate,
        validator: validator,
    }); },
    __typeEmits: {},
    __typeProps: {},
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    __typeEmits: {},
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
