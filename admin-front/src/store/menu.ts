import { defineStore } from "pinia";
import { ref } from "vue";
import Menu from "@/core/data/menu.json";
// import sidebarlist from "@/types/sidebarlist"
import menu from "@/types/menu"
interface searchdatas {
    icon1: string,
    icon2: string,
    path: string,
    title: string
}
interface search {
    icon1: string,
    icon2: string,
    path: string,
    title: string,
    bookmark: string
}
export const useMenuStore = defineStore("menu", () => {
    const data1 = ref(Menu.data);

    const data: menu[] = (JSON.parse(JSON.stringify(Menu.data)))

    const togglesidebar = ref<boolean>(true);
    const activeoverlay = ref<boolean>(true);
    const customizer = ref<string>("");
    const searchData = ref<searchdatas[]>([]);
    const searchDatas = ref<search[]>([]);
    const searchOpen = ref<boolean>(false);
    const hideRightArrowRTL = ref<boolean>(false)
    const hideLeftArrowRTL = ref<boolean>(true)
    const hideRightArrow = ref<boolean>(true)
    const hideLeftArrow = ref<boolean>(true)
    const width = ref<number>(0)
    const height = ref<number>(0)
    const margin = ref<number>(0)
    const menuWidth = ref<number>(0)
    const perentName = ref<string>('')
    const subName = ref<string>('')
    const childName = ref<string>('')
    const bodyToggle = ref(false)
    const perentToggle = ref<boolean>(false)
    const subToggle = ref<boolean>(false)
    const childToggle = ref<boolean>(false)

    function toggle_sidebar() {
        togglesidebar.value = !togglesidebar.value;
        if (window.innerWidth < 991) {
            activeoverlay.value = true;
        } else {
            activeoverlay.value = false;
        }
        activeoverlay.value = false;
    }

    function subMenuToggle(Name: string) {
        perentName.value = perentName.value != Name ? Name : ""
        perentToggle.value = perentName.value != "" ? true : false
    }
    function subChildMenu(subTitle: string) {
        subName.value = subName.value != subTitle ? subTitle : ''
        subToggle.value = subName.value != "" ? true : false
    }
    function childMenu(childTitle: string) {
        childName.value = childName.value != childTitle ? childTitle : "";
        childToggle.value = childName.value != '' ? true : false

    }
    function searchTerm(term: any) {

        const items: any = [];

        const searchval = term.toLowerCase()
        console.log('v', data1);
        data1.value.filter((menuItems: any) => {
            console.log('jin', menuItems.headTitle1);
            if (menuItems.title?.toLowerCase().includes(term) && menuItems.type === 'link') {
                items.push(menuItems);
            }
            menuItems.children?.filter((subItems: any) => {
                if (subItems.title?.toLowerCase().includes(term) && subItems.type === 'link') {
                    subItems.icon1 = menuItems.icon1
                    items.push(subItems);

                }
                if (!subItems.children) return false;
                subItems.children?.filter((suSubItems: any) => {
                    if (suSubItems.title?.toLowerCase().includes(term)) {
                        suSubItems.icon1 = menuItems.icon1
                        items.push(suSubItems);
                    }
                })

            })
            searchData.value = items;
        })
    }
    function searchterm(terms: any) {
        const items: any = [];
        const searchval = terms.toLowerCase()
        console.log('v', data1);
        data1.value.filter((menuItems: any) => {
            if (menuItems.title?.toLowerCase().includes(terms) && menuItems.type === 'link') {
                items.push(menuItems);
            }
            menuItems.children?.filter((subItems: any) => {
                if (subItems.title?.toLowerCase().includes(terms) && subItems.type === 'link') {
                    subItems.icon1 = menuItems.icon1
                    items.push(subItems);

                }
                if (!subItems.children) return false;
                subItems.children?.filter((suSubItems: any) => {
                    if (suSubItems.title?.toLowerCase().includes(terms)) {
                        suSubItems.icon1 = menuItems.icon1
                        items.push(suSubItems);
                    }
                })

            })
            searchDatas.value = items;
        })

    }

    function setNavActive(item: any) {
        if (!item.active) {
            console.log("jimin", data);

            data.forEach((a: any) => {
                console.log("jimin", data);
                if (data.includes(item))
                    a.active = false;
                if (!a.children) return false;
                a.children.forEach((b: any) => {
                    if (a.children.includes(item)) {
                        b.active = false;
                    }
                });
            });
        }
        item.active = !item.active;
        if (item.active) {
            bodyToggle.value = true
        }
        else {
            bodyToggle.value = false
        }
    }
    //   function setActiveRoute(item: any) {
    //     data.value.filter(menuItem => {
    //       menuItem.children?.filter(menu => {
    //         if (menu! == item)
    //           item.active = false;
    //         if (menu.children && menu.children.includes(item))

    //           item.active = true;
    //         if (menu.children) {
    //           menu.children.filter(submenuItems => {
    //           });
    //         }
    //       })

    //     });
    //   }
    return {
        data,
        togglesidebar,
        activeoverlay,
        toggle_sidebar,
        setNavActive,
        customizer,
        searchTerm,
        searchterm,
        searchData,
        searchOpen,
        hideRightArrowRTL,
        hideLeftArrowRTL,
        hideRightArrow,
        hideLeftArrow,
        width,
        height,
        margin,
        menuWidth,
        searchDatas,
        // setActiveRoute,
        data1,
        bodyToggle,
        subMenuToggle,
        subChildMenu,
        childMenu,
        perentName,
        subName,
        childName,
        perentToggle,
        subToggle,
        childToggle
    };
});
