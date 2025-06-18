import HttpRepository from '@/core/http/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';
import Member from '@/features/member/entity/Member';
import PasswordChange from '@/features/member/entity/PasswordChange';

@singleton()
export default class MemberRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}

  public async getMyInfo(): Promise<Member> {
    const response = await this.httpRepository.get({
      path: '/api/v1/members/my',
    });

    return Member.fromResponse(response);
  }

  public async changePassword(passwordChange: PasswordChange): Promise<void> {
    await this.httpRepository.patch({
      path: '/api/v1/members/password',
      body: passwordChange,
    });
  }
}
