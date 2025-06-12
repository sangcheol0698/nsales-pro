import HttpRepository from '@/core/http/HttpRepository.ts';
import type Login from '@/features/auth/entity/Login.ts';
import type Register from '@/features/auth/entity/Register.ts';
import type FindPassword from '@/features/auth/entity/FindPassword.ts';
import type SetPassword from '@/features/auth/entity/SetPassword.ts';
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

  public async findPassword(data: FindPassword) {
    await this.httpRepository.post({
      path: '/api/v1/auths/find-password',
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
