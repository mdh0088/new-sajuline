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
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
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
var vue_1 = require("vue");
var useAuth_1 = require("~/composables/auth/useAuth");
var useValidation_1 = require("~/composables/validation/useValidation");
var emit = defineEmits();
// 컴포저블
var _a = (0, useAuth_1.useAuth)(), login = _a.login, isLoginLoading = _a.isLoginLoading;
var _b = (0, useValidation_1.useValidation)(), validateRequired = _b.validateRequired, validateMinLength = _b.validateMinLength, validateEmailFormat = _b.validateEmailFormat;
// 반응형 데이터
var formData = (0, vue_1.reactive)({
    user_id: '',
    password: '',
    rememberMe: false
});
var errors = (0, vue_1.reactive)({
    user_id: '',
    password: '',
    general: ''
});
var isLoading = (0, vue_1.computed)(function () { return isLoginLoading.value; });
// 유효성 검증
var validateForm = function () {
    // 에러 초기화
    Object.keys(errors).forEach(function (key) {
        errors[key] = '';
    });
    var isValid = true;
    // 사용자 ID 검증
    if (!validateRequired(formData.user_id)) {
        errors.user_id = '사용자 ID 또는 이메일을 입력해주세요.';
        isValid = false;
    }
    else if (formData.user_id.includes('@')) {
        // 이메일 형식 검증
        if (!validateEmailFormat(formData.user_id)) {
            errors.user_id = '올바른 이메일 형식을 입력해주세요.';
            isValid = false;
        }
    }
    else {
        // 사용자 ID 검증
        if (!validateMinLength(formData.user_id, 4)) {
            errors.user_id = '사용자 ID는 4자 이상 입력해주세요.';
            isValid = false;
        }
    }
    // 비밀번호 검증
    if (!validateRequired(formData.password)) {
        errors.password = '비밀번호를 입력해주세요.';
        isValid = false;
    }
    else if (!validateMinLength(formData.password, 6)) {
        errors.password = '비밀번호는 6자 이상 입력해주세요.';
        isValid = false;
    }
    return isValid;
};
// 에러 클리어
var clearError = function (field) {
    if (errors[field]) {
        errors[field] = '';
    }
    if (errors.general) {
        errors.general = '';
    }
};
// 로그인 제출
var handleSubmit = function () { return __awaiter(void 0, void 0, void 0, function () {
    var result, error_1;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                if (!validateForm()) {
                    return [2 /*return*/];
                }
                _a.label = 1;
            case 1:
                _a.trys.push([1, 3, , 4]);
                return [4 /*yield*/, login({
                        user_id: formData.user_id,
                        password: formData.password
                    })];
            case 2:
                result = _a.sent();
                if (result.success) {
                    // 로그인 성공
                    emit('success');
                }
                else {
                    // 로그인 실패
                    errors.general = result.error || '로그인에 실패했습니다.';
                }
                return [3 /*break*/, 4];
            case 3:
                error_1 = _a.sent();
                errors.general = (error_1 === null || error_1 === void 0 ? void 0 : error_1.message) || '로그인 중 오류가 발생했습니다.';
                return [3 /*break*/, 4];
            case 4: return [2 /*return*/];
        }
    });
}); };
// 비밀번호 찾기
var handleForgotPassword = function () {
    emit('forgotPassword');
};
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_ctx = {};
var __VLS_elements;
var __VLS_components;
var __VLS_directives;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_elements.form, __VLS_elements.form)(__assign({ onSubmit: (__VLS_ctx.handleSubmit) }, { class: "space-y-5" }));
// @ts-ignore
[handleSubmit,];
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
__VLS_asFunctionalElement(__VLS_elements.label, __VLS_elements.label)(__assign({ for: "user_id" }, { class: "block text-sm font-medium text-white/80 mb-2" }));
var __VLS_0 = {}.ElInput;
/** @type {[typeof __VLS_components.ElInput, typeof __VLS_components.elInput, ]} */ ;
// @ts-ignore
ElInput;
// @ts-ignore
var __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0(__assign(__assign(__assign({ 'onInput': {} }, { id: "user_id", modelValue: (__VLS_ctx.formData.user_id), type: "text", placeholder: "사용자 ID 또는 이메일을 입력해주세요", autocomplete: "username" }), { class: "auth-input-wrapper" }), { class: ({ 'error': __VLS_ctx.errors.user_id }) })));
var __VLS_2 = __VLS_1.apply(void 0, __spreadArray([__assign(__assign(__assign({ 'onInput': {} }, { id: "user_id", modelValue: (__VLS_ctx.formData.user_id), type: "text", placeholder: "사용자 ID 또는 이메일을 입력해주세요", autocomplete: "username" }), { class: "auth-input-wrapper" }), { class: ({ 'error': __VLS_ctx.errors.user_id }) })], __VLS_functionalComponentArgsRest(__VLS_1), false));
var __VLS_4;
var __VLS_5;
var __VLS_6 = ({ input: {} },
    { onInput: function () {
            var _a = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                _a[_i] = arguments[_i];
            }
            var $event = _a[0];
            __VLS_ctx.clearError('user_id');
            // @ts-ignore
            [formData, errors, clearError,];
        } });
var __VLS_3;
if (__VLS_ctx.errors.user_id) {
    // @ts-ignore
    [errors,];
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "text-red-400 text-sm mt-1" }));
    (__VLS_ctx.errors.user_id);
    // @ts-ignore
    [errors,];
}
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)({});
__VLS_asFunctionalElement(__VLS_elements.label, __VLS_elements.label)(__assign({ for: "password" }, { class: "block text-sm font-medium text-white/80 mb-2" }));
var __VLS_8 = {}.ElInput;
/** @type {[typeof __VLS_components.ElInput, typeof __VLS_components.elInput, ]} */ ;
// @ts-ignore
ElInput;
// @ts-ignore
var __VLS_9 = __VLS_asFunctionalComponent(__VLS_8, new __VLS_8(__assign(__assign(__assign({ 'onInput': {} }, { id: "password", modelValue: (__VLS_ctx.formData.password), type: "password", placeholder: "비밀번호를 입력해주세요", autocomplete: "current-password", showPassword: true }), { class: "auth-input-wrapper" }), { class: ({ 'error': __VLS_ctx.errors.password }) })));
var __VLS_10 = __VLS_9.apply(void 0, __spreadArray([__assign(__assign(__assign({ 'onInput': {} }, { id: "password", modelValue: (__VLS_ctx.formData.password), type: "password", placeholder: "비밀번호를 입력해주세요", autocomplete: "current-password", showPassword: true }), { class: "auth-input-wrapper" }), { class: ({ 'error': __VLS_ctx.errors.password }) })], __VLS_functionalComponentArgsRest(__VLS_9), false));
var __VLS_12;
var __VLS_13;
var __VLS_14 = ({ input: {} },
    { onInput: function () {
            var _a = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                _a[_i] = arguments[_i];
            }
            var $event = _a[0];
            __VLS_ctx.clearError('password');
            // @ts-ignore
            [formData, errors, clearError,];
        } });
var __VLS_11;
if (__VLS_ctx.errors.password) {
    // @ts-ignore
    [errors,];
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "text-red-400 text-sm mt-1" }));
    (__VLS_ctx.errors.password);
    // @ts-ignore
    [errors,];
}
if (__VLS_ctx.errors.general) {
    // @ts-ignore
    [errors,];
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "p-3 bg-red-500/10 border border-red-500/30 rounded-lg" }));
    __VLS_asFunctionalElement(__VLS_elements.p, __VLS_elements.p)(__assign({ class: "text-red-400 text-sm" }));
    (__VLS_ctx.errors.general);
    // @ts-ignore
    [errors,];
}
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "flex items-center justify-between py-2" }));
var __VLS_16 = {}.ElCheckbox;
/** @type {[typeof __VLS_components.ElCheckbox, typeof __VLS_components.elCheckbox, typeof __VLS_components.ElCheckbox, typeof __VLS_components.elCheckbox, ]} */ ;
// @ts-ignore
ElCheckbox;
// @ts-ignore
var __VLS_17 = __VLS_asFunctionalComponent(__VLS_16, new __VLS_16(__assign({ modelValue: (__VLS_ctx.formData.rememberMe) }, { class: "auth-checkbox-wrapper" })));
var __VLS_18 = __VLS_17.apply(void 0, __spreadArray([__assign({ modelValue: (__VLS_ctx.formData.rememberMe) }, { class: "auth-checkbox-wrapper" })], __VLS_functionalComponentArgsRest(__VLS_17), false));
var __VLS_20 = __VLS_19.slots.default;
// @ts-ignore
[formData,];
var __VLS_19;
__VLS_asFunctionalElement(__VLS_elements.button, __VLS_elements.button)(__assign(__assign({ onClick: (__VLS_ctx.handleForgotPassword) }, { type: "button" }), { class: "text-sm text-purple-400 hover:text-purple-300 hover:underline transition-colors duration-300" }));
// @ts-ignore
[handleForgotPassword,];
var __VLS_21 = {}.ElButton;
/** @type {[typeof __VLS_components.ElButton, typeof __VLS_components.elButton, typeof __VLS_components.ElButton, typeof __VLS_components.elButton, ]} */ ;
// @ts-ignore
ElButton;
// @ts-ignore
var __VLS_22 = __VLS_asFunctionalComponent(__VLS_21, new __VLS_21(__assign({ type: "primary", loading: (__VLS_ctx.isLoading), nativeType: "submit" }, { class: "w-full py-4 font-bold rounded-xl auth-btn-primary" })));
var __VLS_23 = __VLS_22.apply(void 0, __spreadArray([__assign({ type: "primary", loading: (__VLS_ctx.isLoading), nativeType: "submit" }, { class: "w-full py-4 font-bold rounded-xl auth-btn-primary" })], __VLS_functionalComponentArgsRest(__VLS_22), false));
var __VLS_25 = __VLS_24.slots.default;
// @ts-ignore
[isLoading,];
if (!__VLS_ctx.isLoading) {
    // @ts-ignore
    [isLoading,];
    var __VLS_26 = {}.Icon;
    /** @type {[typeof __VLS_components.Icon, ]} */ ;
    // @ts-ignore
    Icon;
    // @ts-ignore
    var __VLS_27 = __VLS_asFunctionalComponent(__VLS_26, new __VLS_26(__assign({ name: "mdi:login" }, { class: "w-5 h-5" })));
    var __VLS_28 = __VLS_27.apply(void 0, __spreadArray([__assign({ name: "mdi:login" }, { class: "w-5 h-5" })], __VLS_functionalComponentArgsRest(__VLS_27), false));
}
(__VLS_ctx.isLoading ? '로그인 중...' : '로그인');
// @ts-ignore
[isLoading,];
var __VLS_24;
/** @type {__VLS_StyleScopedClasses['space-y-5']} */ ;
/** @type {__VLS_StyleScopedClasses['block']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white/80']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-2']} */ ;
/** @type {__VLS_StyleScopedClasses['auth-input-wrapper']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-400']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-1']} */ ;
/** @type {__VLS_StyleScopedClasses['block']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-medium']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white/80']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-2']} */ ;
/** @type {__VLS_StyleScopedClasses['auth-input-wrapper']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-400']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['mt-1']} */ ;
/** @type {__VLS_StyleScopedClasses['p-3']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-red-500/10']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-red-500/30']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['text-red-400']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['py-2']} */ ;
/** @type {__VLS_StyleScopedClasses['auth-checkbox-wrapper']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-purple-400']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-purple-300']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:underline']} */ ;
/** @type {__VLS_StyleScopedClasses['transition-colors']} */ ;
/** @type {__VLS_StyleScopedClasses['duration-300']} */ ;
/** @type {__VLS_StyleScopedClasses['w-full']} */ ;
/** @type {__VLS_StyleScopedClasses['py-4']} */ ;
/** @type {__VLS_StyleScopedClasses['font-bold']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['auth-btn-primary']} */ ;
/** @type {__VLS_StyleScopedClasses['w-5']} */ ;
/** @type {__VLS_StyleScopedClasses['h-5']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () { return ({
        formData: formData,
        errors: errors,
        isLoading: isLoading,
        clearError: clearError,
        handleSubmit: handleSubmit,
        handleForgotPassword: handleForgotPassword,
    }); },
    __typeEmits: {},
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    __typeEmits: {},
});
; /* PartiallyEnd: #4569/main.vue */
