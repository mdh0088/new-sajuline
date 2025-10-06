<template>
  <div class="container-fluid p-0">
    <div class="row m-0">
      <div class="col-12 p-0">
        <div class="login-card login-dark">
          <div>
            <div>
              <router-link class="logo" to="/">
                <img class="img-fluid for-light"
                     src="@/assets/images/logo/logo-1.png"
                     alt="looginpage">
                <img class="img-fluid for-dark"
                     src="@/assets/images/logo/logo.png" alt="looginpage">
              </router-link>
            </div>
            <div class="login-main">
              <form class="theme-form" @submit.prevent="">
                <div class="form-group">
                  <label class="col-form-label">User Id</label>
                  <input v-model="loginInfo.user_id" class="form-control" type="text" placeholder="login id">
                </div>
                <div class="form-group">
                  <label class="col-form-label">Password</label>
                  <div class="form-input position-relative">
                    <input v-model="loginInfo.password" :type="type" class="form-control" placeholder="*********">
                    <div class="show-hide"><span class="show" @click="showPassword"> </span></div>
                  </div>
                </div>
                <div class="form-group mb-0">
                  <div class="text-end mt-3">
                    <button class="btn btn-primary btn-block w-100" type="submit" @click="loginProcess">
                      Log in
                    </button>
                  </div>
                </div>

              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup>
import { ref, inject } from "vue"
import {doLogin} from "@/views/pages/login/loginPage"
import * as swal from '@/commonUtils/swal';
import type { LoginRequest } from '@/types/auth';

const type = ref<string>('password')

const loginInfo = ref<LoginRequest>({
  user_id:"",
  password:""
})

const router = inject('$router');

function showPassword() {
  if (type.value === 'password') {
    type.value = 'text';
  } else {
    type.value = 'password';
  }
}
const loginProcess = async () => {

  if (loginInfo.value.user_id === '') {
    swal.swalAlert('아이디를 입력해주세요.', 'warning');
  } else if (loginInfo.value.password === '') {
    swal.swalAlert('비밀번호를 입력해주세요.', 'warning');
  } else {
    loginInfo.value.user_id = loginInfo.value.user_id.trim();
    await doLogin(router, loginInfo);
  }
}
</script>