import { formatPhoneNumber } from '@/core/utils/PhoneUtils.ts';

export default class EmployeeMyInfo {
  name: string;
  teamName: string;
  email: string;
  phone: string;
  birthDate: string;
  joinDate: string;

  constructor(data: {
    name: string;
    teamName: string;
    email: string;
    phone: string;
    birthDate: string;
    joinDate: string;
  }) {
    this.name = data.name;
    this.teamName = data.teamName;
    this.email = data.email;
    this.phone = data.phone;
    this.birthDate = data.birthDate;
    this.joinDate = data.joinDate;
  }

  static fromResponse(response: any): EmployeeMyInfo {
    return new EmployeeMyInfo({
      name: response.name || '',
      teamName: response.teamName || '',
      email: response.email || '',
      phone: formatPhoneNumber(response.phone),
      birthDate: response.birthDate || '',
      joinDate: response.joinDate || '',
    });
  }
}
