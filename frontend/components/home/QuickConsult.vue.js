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
var props = withDefaults(defineProps(), {
    categories: function () { return [
        { name: '연애', path: '/categories/love', icon: '❤️' },
        { name: '직장', path: '/categories/work', icon: '💼' },
        { name: '재물', path: '/categories/money', icon: '💰' }
    ]; }
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_withDefaultsArg = (function (t) { return t; })({
    categories: function () { return [
        { name: '연애', path: '/categories/love', icon: '❤️' },
        { name: '직장', path: '/categories/work', icon: '💼' },
        { name: '재물', path: '/categories/money', icon: '💰' }
    ]; }
});
var __VLS_ctx = {};
var __VLS_elements;
var __VLS_components;
var __VLS_directives;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_elements.section, __VLS_elements.section)(__assign({ class: "px-5 py-6" }));
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "flex justify-between items-center mb-4" }));
__VLS_asFunctionalElement(__VLS_elements.h2, __VLS_elements.h2)(__assign({ class: "text-xl font-bold" }));
var __VLS_0 = {}.NuxtLink;
/** @type {[typeof __VLS_components.NuxtLink, typeof __VLS_components.NuxtLink, ]} */ ;
// @ts-ignore
NuxtLink;
// @ts-ignore
var __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0(__assign({ to: "/categories" }, { class: "text-sm text-purple-300 flex items-center gap-1 hover:text-purple-200 transition-colors" })));
var __VLS_2 = __VLS_1.apply(void 0, __spreadArray([__assign({ to: "/categories" }, { class: "text-sm text-purple-300 flex items-center gap-1 hover:text-purple-200 transition-colors" })], __VLS_functionalComponentArgsRest(__VLS_1), false));
var __VLS_4 = __VLS_3.slots.default;
var __VLS_3;
__VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "grid grid-cols-3 gap-3 max-w-md mx-auto" }));
for (var _i = 0, _a = __VLS_getVForSourceType((__VLS_ctx.categories)); _i < _a.length; _i++) {
    var _b = _a[_i], category = _b[0], index = _b[1];
    // @ts-ignore
    [categories,];
    var __VLS_5 = {}.NuxtLink;
    /** @type {[typeof __VLS_components.NuxtLink, typeof __VLS_components.NuxtLink, ]} */ ;
    // @ts-ignore
    NuxtLink;
    // @ts-ignore
    var __VLS_6 = __VLS_asFunctionalComponent(__VLS_5, new __VLS_5(__assign({ key: (index), to: (category.path) }, { class: "relative p-5 bg-white/3 border border-white/10 rounded-2xl text-center cursor-pointer transition-all duration-300 hover:bg-white/5 active:scale-98 group overflow-hidden" })));
    var __VLS_7 = __VLS_6.apply(void 0, __spreadArray([__assign({ key: (index), to: (category.path) }, { class: "relative p-5 bg-white/3 border border-white/10 rounded-2xl text-center cursor-pointer transition-all duration-300 hover:bg-white/5 active:scale-98 group overflow-hidden" })], __VLS_functionalComponentArgsRest(__VLS_6), false));
    var __VLS_9 = __VLS_8.slots.default;
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "absolute inset-0 bg-gradient-to-br from-purple-600/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" }));
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "relative z-10" }));
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "w-14 h-14 mx-auto mb-3 bg-gradient-to-br from-purple-600/20 to-purple-700/10 rounded-2xl flex items-center justify-center text-2xl border border-purple-600/20" }));
    (category.icon);
    __VLS_asFunctionalElement(__VLS_elements.div, __VLS_elements.div)(__assign({ class: "text-sm font-semibold text-white/90" }));
    (category.name);
    var __VLS_8;
}
/** @type {__VLS_StyleScopedClasses['px-5']} */ ;
/** @type {__VLS_StyleScopedClasses['py-6']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-between']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-4']} */ ;
/** @type {__VLS_StyleScopedClasses['text-xl']} */ ;
/** @type {__VLS_StyleScopedClasses['font-bold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['text-purple-300']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-1']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:text-purple-200']} */ ;
/** @type {__VLS_StyleScopedClasses['transition-colors']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['grid-cols-3']} */ ;
/** @type {__VLS_StyleScopedClasses['gap-3']} */ ;
/** @type {__VLS_StyleScopedClasses['max-w-md']} */ ;
/** @type {__VLS_StyleScopedClasses['mx-auto']} */ ;
/** @type {__VLS_StyleScopedClasses['relative']} */ ;
/** @type {__VLS_StyleScopedClasses['p-5']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-white/3']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-white/10']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['text-center']} */ ;
/** @type {__VLS_StyleScopedClasses['cursor-pointer']} */ ;
/** @type {__VLS_StyleScopedClasses['transition-all']} */ ;
/** @type {__VLS_StyleScopedClasses['duration-300']} */ ;
/** @type {__VLS_StyleScopedClasses['hover:bg-white/5']} */ ;
/** @type {__VLS_StyleScopedClasses['active:scale-98']} */ ;
/** @type {__VLS_StyleScopedClasses['group']} */ ;
/** @type {__VLS_StyleScopedClasses['overflow-hidden']} */ ;
/** @type {__VLS_StyleScopedClasses['absolute']} */ ;
/** @type {__VLS_StyleScopedClasses['inset-0']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-gradient-to-br']} */ ;
/** @type {__VLS_StyleScopedClasses['from-purple-600/10']} */ ;
/** @type {__VLS_StyleScopedClasses['to-transparent']} */ ;
/** @type {__VLS_StyleScopedClasses['opacity-0']} */ ;
/** @type {__VLS_StyleScopedClasses['group-hover:opacity-100']} */ ;
/** @type {__VLS_StyleScopedClasses['transition-opacity']} */ ;
/** @type {__VLS_StyleScopedClasses['duration-300']} */ ;
/** @type {__VLS_StyleScopedClasses['relative']} */ ;
/** @type {__VLS_StyleScopedClasses['z-10']} */ ;
/** @type {__VLS_StyleScopedClasses['w-14']} */ ;
/** @type {__VLS_StyleScopedClasses['h-14']} */ ;
/** @type {__VLS_StyleScopedClasses['mx-auto']} */ ;
/** @type {__VLS_StyleScopedClasses['mb-3']} */ ;
/** @type {__VLS_StyleScopedClasses['bg-gradient-to-br']} */ ;
/** @type {__VLS_StyleScopedClasses['from-purple-600/20']} */ ;
/** @type {__VLS_StyleScopedClasses['to-purple-700/10']} */ ;
/** @type {__VLS_StyleScopedClasses['rounded-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['flex']} */ ;
/** @type {__VLS_StyleScopedClasses['items-center']} */ ;
/** @type {__VLS_StyleScopedClasses['justify-center']} */ ;
/** @type {__VLS_StyleScopedClasses['text-2xl']} */ ;
/** @type {__VLS_StyleScopedClasses['border']} */ ;
/** @type {__VLS_StyleScopedClasses['border-purple-600/20']} */ ;
/** @type {__VLS_StyleScopedClasses['text-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['font-semibold']} */ ;
/** @type {__VLS_StyleScopedClasses['text-white/90']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () { return ({}); },
    __typeProps: {},
    props: {},
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    __typeProps: {},
    props: {},
});
; /* PartiallyEnd: #4569/main.vue */
