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
Object.defineProperty(exports, "__esModule", { value: true });
var models_1 = require("~/types/user/models");
var useValidation_1 = require("~/composables/validation/useValidation");
var useUserQueries_1 = require("~/composables/api/useUserQueries");
// defineModel로 간단하게 처리
var signupFormData = defineModel('signupFormData', { required: true });
// Step2 자체 검증 로직
var _a = (0, useValidation_1.useValidation)(), validateNickname = _a.validateNickname, validatePhone = _a.validatePhone;
var _b = (0, useUserQueries_1.useUserQueries)(), useNicknameAvailability = _b.useNicknameAvailability, usePhoneAvailability = _b.usePhoneAvailability;
// 닉네임 중복 검사
var nicknameAvailabilityQuery = useNicknameAvailability(computed(function () { return signupFormData.value.nickname || ''; }), {
    enabled: computed(function () { return !!signupFormData.value.nickname && signupFormData.value.nickname.length >= 2; })
});
// 휴대폰 중복 검사
var phoneAvailabilityQuery = usePhoneAvailability(computed(function () { return signupFormData.value.phone || ''; }), {
    enabled: computed(function () { return !!signupFormData.value.phone && /^010\d{8}$/.test(signupFormData.value.phone); })
});
// 개별 필드 검증
var nicknameValidator = computed(function () { return validateNickname(signupFormData.value.nickname, nicknameAvailabilityQuery); });
var phoneValidator = computed(function () { return validatePhone(signupFormData.value.phone, phoneAvailabilityQuery); });
// Step2 종합 검증 결과
var validator = computed(function () { return ({
    nicknameValidator: nicknameValidator,
    phoneValidator: phoneValidator,
    isValid: nicknameValidator.value.result.value.isValid &&
        phoneValidator.value.result.value.isValid
}); });
// 휴대폰 번호 입력 처리
var handlePhoneInput = function (event) {
    var target = event.target;
    // 숫자만 허용하고 11자리로 제한
    var value = target.value.replace(/[^0-9]/g, '');
    if (value.length > 11) {
        value = value.slice(0, 11);
    }
    signupFormData.value.phone = value;
};
// 인증번호 전송 (이 컴포넌트에서 직접 처리)
var sendVerificationCode = function () {
    // TODO: 휴대폰 인증 로직 구현
    console.log('인증번호 전송:', signupFormData.value.phone);
};
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
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-wrapper" }));
__VLS_asFunctionalElement(__VLS_elements.input, __VLS_elements.input)(__assign(__assign(__assign({ value: (__VLS_ctx.signupFormData.nickname), type: "text" }, { class: "input-field" }), { placeholder: "닉네임을 입력해주세요" }), { class: ({
        error: !__VLS_ctx.validator.nicknameValidator.value.result.value.isValid && __VLS_ctx.signupFormData.nickname,
        success: __VLS_ctx.validator.nicknameValidator.value.result.value.isValid && __VLS_ctx.signupFormData.nickname
    }) }));
// @ts-ignore
[signupFormData, signupFormData, signupFormData, validator, validator,];
if (__VLS_ctx.validator.nicknameValidator.value.result.value.isChecking) {
    // @ts-ignore
    [validator,];
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)(__assign({ class: "checking-indicator" }));
}
if (__VLS_ctx.validator.nicknameValidator.value.result.value.message) {
    // @ts-ignore
    [validator,];
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "validation-text" }, { class: ({
            'error-text': !__VLS_ctx.validator.nicknameValidator.value.result.value.isValid,
            'success-text': __VLS_ctx.validator.nicknameValidator.value.result.value.isValid && __VLS_ctx.signupFormData.nickname
        }) }));
    // @ts-ignore
    [signupFormData, validator, validator,];
    (__VLS_ctx.validator.nicknameValidator.value.result.value.message);
    // @ts-ignore
    [validator,];
}
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-group" }));
__VLS_asFunctionalElement(__VLS_elements.label, __VLS_elements.label)(__assign({ class: "input-label" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-with-button" }));
__VLS_asFunctionalElement(__VLS_elements.input, __VLS_elements.input)(__assign(__assign(__assign(__assign({ onInput: (__VLS_ctx.handlePhoneInput) }, { type: "tel" }), { class: "input-field" }), { placeholder: "01012345678", maxlength: "11" }), { class: ({
        error: !__VLS_ctx.validator.phoneValidator.value.result.value.isValid && __VLS_ctx.signupFormData.phone,
        success: __VLS_ctx.validator.phoneValidator.value.result.value.isValid && __VLS_ctx.signupFormData.phone
    }) }));
(__VLS_ctx.signupFormData.phone);
// @ts-ignore
[signupFormData, signupFormData, signupFormData, validator, validator, handlePhoneInput,];
__VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)(__assign(__assign({ onClick: (__VLS_ctx.sendVerificationCode) }, { type: "button" }), { class: "verify-button" }));
// @ts-ignore
[sendVerificationCode,];
if (__VLS_ctx.validator.phoneValidator.value.result.value.isChecking) {
    // @ts-ignore
    [validator,];
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)(__assign({ class: "checking-indicator" }));
}
if (__VLS_ctx.validator.phoneValidator.value.result.value.message) {
    // @ts-ignore
    [validator,];
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "validation-text" }, { class: ({
            'error-text': !__VLS_ctx.validator.phoneValidator.value.result.value.isValid,
            'success-text': __VLS_ctx.validator.phoneValidator.value.result.value.isValid && __VLS_ctx.signupFormData.phone
        }) }));
    // @ts-ignore
    [signupFormData, validator, validator,];
    (__VLS_ctx.validator.phoneValidator.value.result.value.message);
    // @ts-ignore
    [validator,];
}
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-group" }));
__VLS_asFunctionalElement(__VLS_elements.label, __VLS_elements.label)(__assign({ class: "input-label" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "gender-select" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.signupFormData.gender = __VLS_ctx.Gender.MALE;
        // @ts-ignore
        [signupFormData, models_1.Gender,];
    } }, { class: "gender-option" }), { class: ({ selected: __VLS_ctx.signupFormData.gender === __VLS_ctx.Gender.MALE }) }));
// @ts-ignore
[signupFormData, models_1.Gender,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "gender-icon" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "gender-label" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.signupFormData.gender = __VLS_ctx.Gender.FEMALE;
        // @ts-ignore
        [signupFormData, models_1.Gender,];
    } }, { class: "gender-option" }), { class: ({ selected: __VLS_ctx.signupFormData.gender === __VLS_ctx.Gender.FEMALE }) }));
// @ts-ignore
[signupFormData, models_1.Gender,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "gender-icon" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "gender-label" }));
/** @type {__VLS_StyleScopedClasses['form-section']} */ ;
/** @type {__VLS_StyleScopedClasses['section-title']} */ ;
/** @type {__VLS_StyleScopedClasses['section-subtitle']} */ ;
/** @type {__VLS_StyleScopedClasses['input-group']} */ ;
/** @type {__VLS_StyleScopedClasses['input-label']} */ ;
/** @type {__VLS_StyleScopedClasses['input-wrapper']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['success']} */ ;
/** @type {__VLS_StyleScopedClasses['checking-indicator']} */ ;
/** @type {__VLS_StyleScopedClasses['validation-text']} */ ;
/** @type {__VLS_StyleScopedClasses['error-text']} */ ;
/** @type {__VLS_StyleScopedClasses['success-text']} */ ;
/** @type {__VLS_StyleScopedClasses['input-group']} */ ;
/** @type {__VLS_StyleScopedClasses['input-label']} */ ;
/** @type {__VLS_StyleScopedClasses['input-with-button']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['success']} */ ;
/** @type {__VLS_StyleScopedClasses['verify-button']} */ ;
/** @type {__VLS_StyleScopedClasses['checking-indicator']} */ ;
/** @type {__VLS_StyleScopedClasses['validation-text']} */ ;
/** @type {__VLS_StyleScopedClasses['error-text']} */ ;
/** @type {__VLS_StyleScopedClasses['success-text']} */ ;
/** @type {__VLS_StyleScopedClasses['input-group']} */ ;
/** @type {__VLS_StyleScopedClasses['input-label']} */ ;
/** @type {__VLS_StyleScopedClasses['gender-select']} */ ;
/** @type {__VLS_StyleScopedClasses['gender-option']} */ ;
/** @type {__VLS_StyleScopedClasses['selected']} */ ;
/** @type {__VLS_StyleScopedClasses['gender-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['gender-label']} */ ;
/** @type {__VLS_StyleScopedClasses['gender-option']} */ ;
/** @type {__VLS_StyleScopedClasses['selected']} */ ;
/** @type {__VLS_StyleScopedClasses['gender-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['gender-label']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () { return ({
        Gender: models_1.Gender,
        signupFormData: signupFormData,
        validator: validator,
        handlePhoneInput: handlePhoneInput,
        sendVerificationCode: sendVerificationCode,
    }); },
    __typeEmits: {},
    __typeProps: {},
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    __typeEmits: {},
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
