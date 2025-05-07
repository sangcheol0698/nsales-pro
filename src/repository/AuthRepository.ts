import HttpRepository from '@/repository/HttpRepository.ts';
import type Login from '@/enity/auth/Login.ts';
import type Register from '@/enity/auth/Register.ts';
import type ForgotPassword from '@/enity/auth/ForgotPassword.ts';

export default class AuthRepository extends HttpRepository {

  public async login(data: Login) {
    await this.post({
      path: '/api/v1/auths/login',
      body: data,
    });
  }

  public async register(data: Register) {
    await this.post({
      path: '/api/v1/auths/register',
      body: data,
    });
  }

  public async forgotPassword(data: ForgotPassword) {
    await this.post({
      path: '/api/v1/auths/forgot-password',
      body: data,
    });
  }

  public async setPassword(data: SetPassword) {
    await this.patch({
      path: '/api/v1/auths/initialize',
      body: data,
    });
  }
}
