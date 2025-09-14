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
var useValidation_1 = require("~/composables/validation/useValidation");
var useUserQueries_1 = require("~/composables/api/useUserQueries");
// defineModel로 간단하게 처리
var signupFormData = defineModel('signupFormData', { required: true });
// Step1 자체 검증 로직
var _a = (0, useValidation_1.useValidation)(), validateEmail = _a.validateEmail, validateUserId = _a.validateUserId, validatePassword = _a.validatePassword;
var _b = (0, useUserQueries_1.useUserQueries)(), useEmailAvailability = _b.useEmailAvailability, useUserIdAvailability = _b.useUserIdAvailability;
// 중복 검사 쿼리들
var emailAvailabilityQuery = useEmailAvailability(computed(function () { return signupFormData.value.email || ''; }), {
    enabled: computed(function () { return !!signupFormData.value.email && signupFormData.value.email.includes('@'); })
});
var userIdAvailabilityQuery = useUserIdAvailability(computed(function () { return signupFormData.value.user_id || ''; }), {
    enabled: computed(function () { return !!signupFormData.value.user_id && signupFormData.value.user_id.length >= 4; })
});
// 개별 필드 검증
var userIdValidator = computed(function () { return validateUserId(signupFormData.value.user_id, userIdAvailabilityQuery); });
var emailValidator = computed(function () { return validateEmail(signupFormData.value.email, emailAvailabilityQuery); });
var passwordValidator = computed(function () { return validatePassword(signupFormData.value.password, signupFormData.value.confirmPassword); });
// Step1 종합 검증 결과
var validator = computed(function () { return ({
    userIdValidator: userIdValidator,
    emailValidator: emailValidator,
    passwordValidator: passwordValidator,
    isValid: userIdValidator.value.result.value.isValid &&
        emailValidator.value.result.value.isValid &&
        passwordValidator.value.passwordResult.value.isValid &&
        passwordValidator.value.confirmResult.value.isValid
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
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-wrapper" }));
__VLS_asFunctionalElement(__VLS_elements.input, __VLS_elements.input)(__assign(__assign({ value: (__VLS_ctx.signupFormData.user_id), type: "text" }, { class: "input-field" }), { placeholder: "4-20자 영문, 숫자, 밑줄(_) 조합 (이메일 형식 불가)" }));
// @ts-ignore
[signupFormData,];
if (__VLS_ctx.validator.userIdValidator.value.result.value.isChecking) {
    // @ts-ignore
    [validator,];
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)(__assign({ class: "checking-indicator" }));
}
__VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "help-text" }));
if (__VLS_ctx.validator.userIdValidator.value.result.value.message) {
    // @ts-ignore
    [validator,];
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "validation-text" }, { class: ({
            'error-text': !__VLS_ctx.validator.userIdValidator.value.result.value.isValid,
            'success-text': __VLS_ctx.validator.userIdValidator.value.result.value.isValid && __VLS_ctx.signupFormData.user_id
        }) }));
    // @ts-ignore
    [signupFormData, validator, validator,];
    (__VLS_ctx.validator.userIdValidator.value.result.value.message);
    // @ts-ignore
    [validator,];
}
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-group" }));
__VLS_asFunctionalElement(__VLS_elements.label, __VLS_elements.label)(__assign({ class: "input-label" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-wrapper" }));
__VLS_asFunctionalElement(__VLS_elements.input, __VLS_elements.input)(__assign(__assign({ type: "email" }, { class: "input-field" }), { placeholder: "example@email.com" }));
(__VLS_ctx.signupFormData.email);
// @ts-ignore
[signupFormData,];
if (__VLS_ctx.validator.emailValidator.value.result.value.isChecking) {
    // @ts-ignore
    [validator,];
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)(__assign({ class: "checking-indicator" }));
}
if (__VLS_ctx.validator.emailValidator.value.result.value.message) {
    // @ts-ignore
    [validator,];
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "validation-text" }, { class: ({
            'error-text': !__VLS_ctx.validator.emailValidator.value.result.value.isValid,
            'success-text': __VLS_ctx.validator.emailValidator.value.result.value.isValid && __VLS_ctx.signupFormData.email
        }) }));
    // @ts-ignore
    [signupFormData, validator, validator,];
    (__VLS_ctx.validator.emailValidator.value.result.value.message);
    // @ts-ignore
    [validator,];
}
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-group" }));
__VLS_asFunctionalElement(__VLS_elements.label, __VLS_elements.label)(__assign({ class: "input-label" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-wrapper" }));
__VLS_asFunctionalElement(__VLS_elements.input, __VLS_elements.input)(__assign(__assign({ type: "password" }, { class: "input-field" }), { placeholder: "8자 이상 영문, 숫자, 특수문자 포함" }));
(__VLS_ctx.signupFormData.password);
// @ts-ignore
[signupFormData,];
if (__VLS_ctx.signupFormData.password) {
    // @ts-ignore
    [signupFormData,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "password-strength" }));
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "strength-bar" }));
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign(__assign({ class: "strength-fill" }, { class: ("strength-".concat(__VLS_ctx.validator.passwordValidator.value.passwordStrength.value.score)) }), { style: ("width: ".concat((__VLS_ctx.validator.passwordValidator.value.passwordStrength.value.score / 4) * 100, "%")) }));
    // @ts-ignore
    [validator, validator,];
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "strength-text" }));
    __VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)(__assign({ class: ("strength-".concat(__VLS_ctx.validator.passwordValidator.value.passwordStrength.value.score)) }));
    // @ts-ignore
    [validator,];
    (['매우 약함', '약함', '보통', '강함', '매우 강함'][__VLS_ctx.validator.passwordValidator.value.passwordStrength.value.score]);
    // @ts-ignore
    [validator,];
}
__VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "help-text" }));
if (__VLS_ctx.validator.passwordValidator.value.passwordResult.value.message) {
    // @ts-ignore
    [validator,];
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "validation-text" }, { class: ({
            'error-text': !__VLS_ctx.validator.passwordValidator.value.passwordResult.value.isValid,
            'success-text': __VLS_ctx.validator.passwordValidator.value.passwordResult.value.isValid && __VLS_ctx.signupFormData.password
        }) }));
    // @ts-ignore
    [signupFormData, validator, validator,];
    (__VLS_ctx.validator.passwordValidator.value.passwordResult.value.message);
    // @ts-ignore
    [validator,];
}
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-group" }));
__VLS_asFunctionalElement(__VLS_elements.label, __VLS_elements.label)(__assign({ class: "input-label" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "input-wrapper" }));
__VLS_asFunctionalElement(__VLS_elements.input, __VLS_elements.input)(__assign(__assign({ type: "password" }, { class: "input-field" }), { placeholder: "비밀번호를 다시 입력해주세요" }));
(__VLS_ctx.signupFormData.confirmPassword);
// @ts-ignore
[signupFormData,];
if (__VLS_ctx.validator.passwordValidator.value.confirmResult.value.message) {
    // @ts-ignore
    [validator,];
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "validation-text" }, { class: ({
            'error-text': !__VLS_ctx.validator.passwordValidator.value.confirmResult.value.isValid,
            'success-text': __VLS_ctx.validator.passwordValidator.value.confirmResult.value.isValid && __VLS_ctx.signupFormData.confirmPassword
        }) }));
    // @ts-ignore
    [signupFormData, validator, validator,];
    (__VLS_ctx.validator.passwordValidator.value.confirmResult.value.message);
    // @ts-ignore
    [validator,];
}
/** @type {__VLS_StyleScopedClasses['form-section']} */ ;
/** @type {__VLS_StyleScopedClasses['section-title']} */ ;
/** @type {__VLS_StyleScopedClasses['section-subtitle']} */ ;
/** @type {__VLS_StyleScopedClasses['input-group']} */ ;
/** @type {__VLS_StyleScopedClasses['input-label']} */ ;
/** @type {__VLS_StyleScopedClasses['input-wrapper']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['checking-indicator']} */ ;
/** @type {__VLS_StyleScopedClasses['help-text']} */ ;
/** @type {__VLS_StyleScopedClasses['validation-text']} */ ;
/** @type {__VLS_StyleScopedClasses['error-text']} */ ;
/** @type {__VLS_StyleScopedClasses['success-text']} */ ;
/** @type {__VLS_StyleScopedClasses['input-group']} */ ;
/** @type {__VLS_StyleScopedClasses['input-label']} */ ;
/** @type {__VLS_StyleScopedClasses['input-wrapper']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['checking-indicator']} */ ;
/** @type {__VLS_StyleScopedClasses['validation-text']} */ ;
/** @type {__VLS_StyleScopedClasses['error-text']} */ ;
/** @type {__VLS_StyleScopedClasses['success-text']} */ ;
/** @type {__VLS_StyleScopedClasses['input-group']} */ ;
/** @type {__VLS_StyleScopedClasses['input-label']} */ ;
/** @type {__VLS_StyleScopedClasses['input-wrapper']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['password-strength']} */ ;
/** @type {__VLS_StyleScopedClasses['strength-bar']} */ ;
/** @type {__VLS_StyleScopedClasses['strength-fill']} */ ;
/** @type {__VLS_StyleScopedClasses['strength-text']} */ ;
/** @type {__VLS_StyleScopedClasses['help-text']} */ ;
/** @type {__VLS_StyleScopedClasses['validation-text']} */ ;
/** @type {__VLS_StyleScopedClasses['error-text']} */ ;
/** @type {__VLS_StyleScopedClasses['success-text']} */ ;
/** @type {__VLS_StyleScopedClasses['input-group']} */ ;
/** @type {__VLS_StyleScopedClasses['input-label']} */ ;
/** @type {__VLS_StyleScopedClasses['input-wrapper']} */ ;
/** @type {__VLS_StyleScopedClasses['input-field']} */ ;
/** @type {__VLS_StyleScopedClasses['validation-text']} */ ;
/** @type {__VLS_StyleScopedClasses['error-text']} */ ;
/** @type {__VLS_StyleScopedClasses['success-text']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () { return ({
        signupFormData: signupFormData,
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
