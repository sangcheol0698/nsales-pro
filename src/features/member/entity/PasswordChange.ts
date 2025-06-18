export default class PasswordChange {
  password: string;
  newPassword: string;
  newPasswordConfirm: string;

  constructor(data: {
    password?: string;
    newPassword?: string;
    newPasswordConfirm?: string;
  } = {}) {
    this.password = data.password || '';
    this.newPassword = data.newPassword || '';
    this.newPasswordConfirm = data.newPasswordConfirm || '';
  }
}
