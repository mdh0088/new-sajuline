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
var props = defineProps();
var emit = defineEmits();
var closeModal = function () {
    emit('close');
};
// 모달이 열릴 때 스크롤 막기
watch(function () { return props.show; }, function (newShow) {
    if (newShow) {
        document.body.style.overflow = 'hidden';
    }
    else {
        document.body.style.overflow = 'auto';
    }
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_ctx = {};
var __VLS_elements;
var __VLS_components;
var __VLS_directives;
if (__VLS_ctx.show) {
    // @ts-ignore
    [show,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ onClick: (__VLS_ctx.closeModal) }, { class: "modal" }));
    // @ts-ignore
    [closeModal,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ onClick: function () { } }, { class: "modal-content" }));
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "modal-header" }));
    __VLS_asFunctionalElement(__VLS_elements.h3, __VLS_elements.h3)(__assign({ class: "modal-title" }));
    __VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)(__assign({ onClick: (__VLS_ctx.closeModal) }, { class: "modal-close" }));
    // @ts-ignore
    [closeModal,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "modal-body" }));
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
    __VLS_asFunctionalDirective(__VLS_directives.vHtml)(null, __assign(__assign({}, __VLS_directiveBindingRestFields), { value: (__VLS_ctx.content) }), null, null);
    // @ts-ignore
    [vHtml, content,];
}
/** @type {__VLS_StyleScopedClasses['modal']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-content']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-header']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-title']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-close']} */ ;
/** @type {__VLS_StyleScopedClasses['modal-body']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () { return ({
        closeModal: closeModal,
    }); },
    __typeEmits: {},
    __typeProps: {},
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    __typeEmits: {},
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
