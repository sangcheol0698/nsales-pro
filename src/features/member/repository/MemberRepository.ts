import HttpRepository from '@/core/http/HttpRepository.ts';
import { inject, singleton } from 'tsyringe';
import type Member from '@/features/member/entity/Member';

@singleton()
export default class MemberRepository {
  constructor(@inject(HttpRepository) private readonly httpRepository: HttpRepository) {}

  public async getMyInfo(): Promise<Member> {
    return await this.httpRepository.get({
      path: '/api/v1/members/my',
    });
  }
}
