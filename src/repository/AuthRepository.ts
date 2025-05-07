import HttpRepository from '@/repository/HttpRepository.ts';
import type Login from '@/enity/auth/Login.ts';
import type Register from '@/enity/auth/Register.ts';
import type ForgotPassword from '@/enity/auth/ForgotPassword.ts';
import type SetPassword from '@/enity/auth/SetPassword.ts';
import { inject, singleton } from 'tsyringe';

@singleton()
export default class AuthRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}

  public async login(data: Login, remember: boolean) {
    await this.httpRepository.post({
      path: '/api/v1/auths/login?remember=' + remember,
      body: data,
    });
  }

  public async register(data: Register) {
    await this.httpRepository.post({
      path: '/api/v1/auths/register',
      body: data,
    });
  }

  public async forgotPassword(data: ForgotPassword) {
    await this.httpRepository.post({
      path: '/api/v1/auths/forgot-password',
      body: data,
    });
  }

  public async setPassword(data: SetPassword) {
    await this.httpRepository.patch({
      path: '/api/v1/auths/initialize',
      body: data,
    });
  }

  public async logout() {
    await this.httpRepository.post({
      path: '/api/v1/auths/logout',
    });
  }
}
