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
// defineModel로 간단하게 처리
var signupFormData = defineModel('signupFormData', { required: true });
var emit = defineEmits();
// 전체 약관 동의 여부
var allTermsAgreed = computed(function () {
    return signupFormData.value.agreeService && signupFormData.value.agreePrivacy && signupFormData.value.is_marketing_agreed;
});
// 필수 약관 동의 검증
var requiredTermsValidator = computed(function () {
    var hasServiceAgree = signupFormData.value.agreeService;
    var hasPrivacyAgree = signupFormData.value.agreePrivacy;
    if (!hasServiceAgree || !hasPrivacyAgree) {
        return {
            isValid: false,
            message: '필수 약관에 동의해주세요.'
        };
    }
    return {
        isValid: true,
        message: '필수 약관 동의가 완료되었습니다.'
    };
});
// Step4 종합 검증 결과
var validator = computed(function () { return ({
    requiredTermsValidator: requiredTermsValidator,
    isValid: requiredTermsValidator.value.isValid
}); });
var toggleAllTerms = function () {
    var newValue = !allTermsAgreed.value;
    signupFormData.value.agreeService = newValue;
    signupFormData.value.agreePrivacy = newValue;
    signupFormData.value.is_marketing_agreed = newValue;
};
var openTermsModal = function (type) {
    emit('open-terms', type);
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
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "terms-section" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ onClick: (__VLS_ctx.toggleAllTerms) }, { class: "terms-all" }));
// @ts-ignore
[toggleAllTerms,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "checkbox" }, { class: ({ checked: __VLS_ctx.allTermsAgreed }) }));
// @ts-ignore
[allTermsAgreed,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "terms-text" }));
__VLS_asFunctionalElement(__VLS_elements.strong, __VLS_elements.strong)({});
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "terms-list" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "terms-item" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.signupFormData.agreeService = !__VLS_ctx.signupFormData.agreeService;
        // @ts-ignore
        [signupFormData, signupFormData,];
    } }, { class: "checkbox terms-check" }), { class: ({ checked: __VLS_ctx.signupFormData.agreeService }) }));
// @ts-ignore
[signupFormData,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "terms-text" }));
__VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)(__assign({ class: "required-badge" }));
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)(__assign(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.openTermsModal('service');
        // @ts-ignore
        [openTermsModal,];
    } }, { href: "#" }), { class: "terms-link" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "terms-item" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.signupFormData.agreePrivacy = !__VLS_ctx.signupFormData.agreePrivacy;
        // @ts-ignore
        [signupFormData, signupFormData,];
    } }, { class: "checkbox terms-check" }), { class: ({ checked: __VLS_ctx.signupFormData.agreePrivacy }) }));
// @ts-ignore
[signupFormData,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "terms-text" }));
__VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)(__assign({ class: "required-badge" }));
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)(__assign(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.openTermsModal('privacy');
        // @ts-ignore
        [openTermsModal,];
    } }, { href: "#" }), { class: "terms-link" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "terms-item" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.signupFormData.is_marketing_agreed = !__VLS_ctx.signupFormData.is_marketing_agreed;
        // @ts-ignore
        [signupFormData, signupFormData,];
    } }, { class: "checkbox terms-check" }), { class: ({ checked: __VLS_ctx.signupFormData.is_marketing_agreed }) }));
// @ts-ignore
[signupFormData,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "terms-text" }));
__VLS_asFunctionalElement(__VLS_elements.span, __VLS_elements.span)(__assign({ style: {} }));
__VLS_asFunctionalElement(__VLS_elements.a, __VLS_elements.a)(__assign(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.openTermsModal('marketing');
        // @ts-ignore
        [openTermsModal,];
    } }, { href: "#" }), { class: "terms-link" }));
if (__VLS_ctx.validator.requiredTermsValidator.value.message) {
    // @ts-ignore
    [validator,];
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "validation-text" }, { class: ({
            'error-text': !__VLS_ctx.validator.requiredTermsValidator.value.isValid,
            'success-text': __VLS_ctx.validator.requiredTermsValidator.value.isValid
        }) }));
    // @ts-ignore
    [validator, validator,];
    (__VLS_ctx.validator.requiredTermsValidator.value.message);
    // @ts-ignore
    [validator,];
}
/** @type {__VLS_StyleScopedClasses['form-section']} */ ;
/** @type {__VLS_StyleScopedClasses['section-title']} */ ;
/** @type {__VLS_StyleScopedClasses['section-subtitle']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-section']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-all']} */ ;
/** @type {__VLS_StyleScopedClasses['checkbox']} */ ;
/** @type {__VLS_StyleScopedClasses['checked']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-text']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-list']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-item']} */ ;
/** @type {__VLS_StyleScopedClasses['checkbox']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-check']} */ ;
/** @type {__VLS_StyleScopedClasses['checked']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-text']} */ ;
/** @type {__VLS_StyleScopedClasses['required-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-link']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-item']} */ ;
/** @type {__VLS_StyleScopedClasses['checkbox']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-check']} */ ;
/** @type {__VLS_StyleScopedClasses['checked']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-text']} */ ;
/** @type {__VLS_StyleScopedClasses['required-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-link']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-item']} */ ;
/** @type {__VLS_StyleScopedClasses['checkbox']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-check']} */ ;
/** @type {__VLS_StyleScopedClasses['checked']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-text']} */ ;
/** @type {__VLS_StyleScopedClasses['terms-link']} */ ;
/** @type {__VLS_StyleScopedClasses['validation-text']} */ ;
/** @type {__VLS_StyleScopedClasses['error-text']} */ ;
/** @type {__VLS_StyleScopedClasses['success-text']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () { return ({
        signupFormData: signupFormData,
        allTermsAgreed: allTermsAgreed,
        validator: validator,
        toggleAllTerms: toggleAllTerms,
        openTermsModal: openTermsModal,
    }); },
    __typeEmits: {},
    __typeProps: {},
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    __typeEmits: {},
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
