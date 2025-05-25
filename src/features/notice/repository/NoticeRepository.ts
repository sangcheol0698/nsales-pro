import { singleton } from 'tsyringe';
import HttpRepository from '@/core/http/HttpRepository.ts';
import type { Notice, NoticeSearch } from '@/features/notice/entity/Notice';

@singleton()
export default class NoticeRepository extends HttpRepository {
  // private readonly BASE_URL = '/api/notices';

  async getNotices(
    params: any
  ): Promise<{ content: NoticeSearch[]; totalPages: number; totalElements: number }> {
    // 실제 애플리케이션에서는 API 호출이 이루어질 것입니다
    // 현재는 목업 데이터를 반환합니다
    const mockNotices: NoticeSearch[] = [
      {
        id: '1',
        title: '시스템 점검 안내',
        content: '시스템 점검이 예정되어 있습니다. 자세한 내용은 공지사항을 확인해주세요.',
        author: '관리자',
        createdAt: '2023-05-15T09:00:00',
        updatedAt: '2023-05-15T09:00:00',
      },
      {
        id: '2',
        title: '신규 기능 업데이트 안내',
        content: '새로운 기능이 추가되었습니다. 자세한 내용은 공지사항을 확인해주세요.',
        author: '관리자',
        createdAt: '2023-05-10T14:30:00',
        updatedAt: '2023-05-10T14:30:00',
      },
      {
        id: '3',
        title: '휴무 안내',
        content: '다음 주 월요일은 휴무입니다. 자세한 내용은 공지사항을 확인해주세요.',
        author: '관리자',
        createdAt: '2023-05-05T11:15:00',
        updatedAt: '2023-05-05T11:15:00',
      },
    ];

    // Simulate pagination
    const page = params.page || 1;
    const limit = params.limit || 10;
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedNotices = mockNotices.slice(startIndex, endIndex);

    return {
      content: paginatedNotices,
      totalPages: Math.ceil(mockNotices.length / limit),
      totalElements: mockNotices.length,
    };
  }

  async getNotice(id: string): Promise<Notice> {
    // 실제 애플리케이션에서는 API 호출이 이루어질 것입니다
    // 현재는 목업 데이터를 반환합니다
    const mockNotices: Notice[] = [
      {
        id: '1',
        title: '시스템 점검 안내',
        content: '시스템 점검이 예정되어 있습니다. 자세한 내용은 공지사항을 확인해주세요.',
        author: '관리자',
        createdAt: '2023-05-15T09:00:00',
        updatedAt: '2023-05-15T09:00:00',
      },
      {
        id: '2',
        title: '신규 기능 업데이트 안내',
        content: '새로운 기능이 추가되었습니다. 자세한 내용은 공지사항을 확인해주세요.',
        author: '관리자',
        createdAt: '2023-05-10T14:30:00',
        updatedAt: '2023-05-10T14:30:00',
      },
      {
        id: '3',
        title: '휴무 안내',
        content: '다음 주 월요일은 휴무입니다. 자세한 내용은 공지사항을 확인해주세요.',
        author: '관리자',
        createdAt: '2023-05-05T11:15:00',
        updatedAt: '2023-05-05T11:15:00',
      },
    ];

    const notice = mockNotices.find((notice) => notice.id === id);
    if (!notice) {
      throw new Error('Notice not found');
    }

    return notice;
  }

  async createNotice(notice: Omit<Notice, 'id' | 'createdAt' | 'updatedAt'>): Promise<Notice> {
    // 실제 애플리케이션에서는 API 호출이 이루어질 것입니다
    // 현재는 목업 데이터를 반환합니다
    return {
      id: Math.random().toString(36).substring(2, 9),
      ...notice,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  }

  async updateNotice(
    id: string,
    notice: Partial<Omit<Notice, 'id' | 'createdAt' | 'updatedAt'>>
  ): Promise<Notice> {
    // 실제 애플리케이션에서는 API 호출이 이루어질 것입니다
    // 현재는 목업 데이터를 반환합니다
    return {
      id,
      title: notice.title || 'Default Title',
      content: notice.content || 'Default Content',
      author: notice.author || 'Default Author',
      createdAt: '2023-05-15T09:00:00',
      updatedAt: new Date().toISOString(),
    };
  }

  async deleteNotice(id: string): Promise<void> {
    // 실제 애플리케이션에서는 API 호출이 이루어질 것입니다.
    // 지금은 반환만 합니다.
    return;
  }
}
