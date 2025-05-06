import HttpRepository from '@/repository/HttpRepository.ts';

export default class AuthRepository extends HttpRepository {
  public async register(data: Register): Promise<void> {
    await this.post('/register', data);
  }

  public login(data: Login) {
    await this.post({
      path: '/api/v1/auths/login',
      body: data,
    })
      .then(() => {
        toast.success('로그인 성공', { description: '환영합니다! 로그인에 성공했습니다.' });
        router.push('/');
      })
      .catch((e: HttpError) => {
        toast.error('로그인 실패', { description: e.getMessage() });
      });
  }

  public async logout(): Promise<void> {
    await this.get('/logout');
  }

  public async setPassword(data: SetPassword): Promise<void> {
    await this.patch('/initialize', data);
  }
}
