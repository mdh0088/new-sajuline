<template>
    <div class="simplebar-wrapper" style="margin: 0px;">
        <div class="simplebar-mask">
            <div class="simplebar-offset" style="right: 0px; bottom: 0px;">
                <div class="simplebar-content-wrapper" style="height: 100%; ">
                    <div class="simplebar-content" style="padding: 0px;">
                        <li class="back-btn"><a href="../../../../../index.html"></a>
                            <div class="mobile-back text-end">
                              <span>Back</span>
                              <i class="fa fa-angle-right ps-2" aria-hidden="true"/>
                            </div>
                        </li>
                        <li class="sidebar-main-title">
                            <div></div>
                        </li>


                        <li class="sidebar-list" v-for="(menu, index) in menuItems" :key="index">
                          <!-- DEPTH 1 START -->
                            <router-link
                                v-if="menu.type == 'link'"
                                :to="menu.path"
                                class="sidebar-link sidebar-title"
                                :class="menu.headTitle1 == store.perentName ? 'active' : ''"
                                @click="store.subMenuToggle(menu.headTitle1)"
                            >
                              <span>
                                <i class="stroke-icon fa" :class="menu.icon"/>
                                {{ menu.korTitle }}
                              </span>
                            </router-link>

                            <a
                                v-if="menu.type == 'headtitle'"
                                class="sidebar-link sidebar-title "
                                :class="menu.headTitle1 == store.perentName ? 'active' : ''"
                                :to="menu.path"
                                @click="store.subMenuToggle(menu.headTitle1)">
                              <span class="cursor-pointer">
                                <i class="stroke-icon fa" :class="menu.icon"/>
                                {{ menu.korTitle}}
                              </span>
                            </a>
                          <!-- DEPTH 1 END -->

                          <!-- DEPTH 2 START -->
                          <ul v-if="menu.type == 'headtitle'"
                              class="sidebar-submenu custom-scrollbar"
                              :class="menu.headTitle1 == store.perentName ? 'd-block' : 'd-none'">

                            <!-- DEPTH 2 제목 -->
                            <li class="sidebar-head">
                              {{ menu.korTitle }}
                            </li>

                            <!-- DEPTH 2 목록 -->
                            <li class="main-submenu"
                                v-for="(child, index) in menu.children"
                                :key="index">

                              <!-- DEPTH 2 다디렉트 링크-->

                              <router-link
                                  v-if="child.type == 'link'"
                                  :to="child.path"
                                  :class="child.title == store.subName ? 'active' : ''"
                                  class="d-flex sidebar-menu"
                                  href="javascript:void(0)"
                                  @click="store.subMenuToggle(child.headTitle1)">
                                {{ child.title }}
                              </router-link>

                              <!-- DEPTH 3 START -->
                              <a
                                  v-if="child.type == 'sub'"
                                  class="d-flex sidebar-menu" href="javascript:void(0)"
                                  :class="child.title == store.subName ? 'active' : ''"
                                  @click="store.subChildMenu(child.title)">
                                {{ child.title }}
                                <svg class="arrow">
                                  <use href="@/assets/svg/icon-sprite.svg#Arrow-right"/>
                                </svg>
                              </a>
                              <ul class="submenu-wrapper"
                                  :class="child.title == store.subName ? 'd-block' : 'd-none'">
                                <li v-for="(subChild, index) in child.children" :key="index">
                                  <router-link
                                      v-if="subChild.type == 'link'"
                                      :to="subChild.path"
                                       @click="store.childMenu(subChild.title)"
                                       :class="[subChild.children ? subChild?.children ? 'submenu-title' : '' : '', subChild?.title == store.childName ? 'active' : '']">
                                    {{ subChild.title }}
                                  </router-link>
                                  <!-- DEPTH 4 START -->
                                  <a
                                      v-if="subChild.type == 'sub'"
                                      class="submenu-title"
                                      href="javascript:void(0)"
                                      :class="[subChild.children ? subChild?.children ? 'submenu-title' : '' : '', subChild?.title == store.childName ? 'active' : '']"
                                      @click="store.childMenu(subChild.title)">
                                    {{subChild.title }}
                                    <i
                                        v-if="subChild.children"
                                        class="fa pull-right mt-1"
                                        v-bind:class="[subChild.active ? 'fa fa-angle-down': 'fa fa-angle-right',]" />
                                  </a>
                                  <ul class="nav-sub-childmenu submenu-content"
                                      :class="subChild?.title == store.childName ? 'd-block' : 'd-none'">
                                    <li v-for="(sub, index) in subChild.children" :key="index">
                                      <router-link
                                          v-if="sub.type == 'link'"
                                          :to="sub.path"
                                          :class="{ 'active': sub.active }">
                                        {{ sub.title }}
                                      </router-link>
                                    </li>
                                  </ul>
                                  <!-- DEPTH 4 END -->
                                </li>
                              </ul>
                              <!-- DEPTH 3 END -->
                            </li>
                          </ul>
                          <!-- DEPTH 2  END -->
                        </li>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script lang="ts" setup>
import { useMenuStore } from "@/store/menu";
const store = useMenuStore();
const menuItems = store.data;

function setNavActive(item: any) {
    store.setNavActive(item);

}
</script>