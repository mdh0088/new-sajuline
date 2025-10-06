import { defineStore } from "pinia";
import { ref, computed } from "vue";
import Layout from "@/core/data/layout.json";
interface Settings {
    layout_type: string;
    layout: string;
    sidebar_icon: string;
    sidebar_setting: string;
}

interface Color {
    layout_version: string;
    primary_color: string;
    secondary_color: string;
}

interface AppConfig {
    settings: Settings;
    color: Color;
}
export const uselayoutStore = defineStore("layout", () => {
    const layout = ref(Layout);
    const boxlayout = ref<boolean>(true);
    const sidebar = ref<string>('default');
    const svg = ref<string>('stroke-svg')
    // const primarycolor = ref<string>("#35bfbf")
    // const secondarycolor = ref<string>('#FF6150')
    function setLayout(val: any) {

        // if (val?.class == "dark-only") {
        //     document.body.classList.contains("light") && document.body.classList.remove("light");
        // } else {
        //     document.body.classList.contains("dark-only") && document.body.classList.remove("dark-only");
        // }
        document.body.className = val.class;
    }
    document.body.setAttribute("main-theme-layout", layout.value.settings.layout_type);
    document.getElementsByTagName("html")[0].setAttribute("dir", layout.value.settings.layout_type);
    const primaryColor: string = localStorage.getItem("primary_color") || layout.value.color.primary_color;
    const secondaryColor = localStorage.getItem("secondary_color") || layout.value.color.secondary_color;
    const layoutVersion = localStorage.getItem("layoutVersion") || layout.value.color.layout_version;

    if (primaryColor || secondaryColor) {
        addStyle(primaryColor, secondaryColor);
        if (layoutVersion)
            document.body.className = layoutVersion;
    }
    function addStyle(primary: string, secondary: string) {
        document.documentElement.style.setProperty("--theme-default", primary);
        document.documentElement.style.setProperty("--theme-secondary", secondary);
    }
    function setLayoutType(layout: any, val: any) {

        document.body.classList.remove("rtl");
        document.body.classList.remove("ltr");
        document.body.classList.remove("boxed");
        document.documentElement.removeAttribute("dir");
        document.body.setAttribute("class", val);
        document.body.setAttribute("main-theme-layout", val);

        layout.settings.layout_type = val;
        document.getElementsByTagName('html')[0].setAttribute('dir', val);
    }

    function setCustomizeSidebarType(val: any) {
        sidebar.value = val.type;
        localStorage.setItem("SidebarType", val);

    }
    function setSvg(svgs: string) {
        svg.value = svgs
        layout.value.settings.sidebar_icon = svgs
    }
    function setColorScheme(color: any) {
        setColor(color);

        // primaryColor = color.primary;
        // secondaryColor = color.secondary
        layout.value.color.layout_version = "light";
        localStorage.setItem("layoutVersion", layout.value.color.layout_version);
    }
    function setColor(color: any) {
        addStyle(color.primary, color.secondary);
        localStorage.setItem("primary_color", color.primary);
        localStorage.setItem("secondary_color", color.secondary);
        window.location.reload();
    }
    return {
        layout,
        setLayout,
        setLayoutType,
        boxlayout,
        setCustomizeSidebarType,
        setSvg,
        svg,
        // primarycolor,
        // secondarycolor,
        setColorScheme
    };
});
