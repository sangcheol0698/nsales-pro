// filepath: /Users/sangcheol/IdeaProjects/nsales-pro/frontend/src/test/unit/http.validation.spec.ts
import { describe, expect, it, vi } from 'vitest';
import * as z from 'zod';
import axios from 'axios';
import AxiosHttpClient from '@/core/http/AxiosHttpClient';
import HttpError from '@/core/http/HttpError';

// axios 모듈을 목킹해서 내부 request 호출을 제어
vi.mock('axios', () => {
  const request = vi.fn();
  const dummyUse = vi.fn();
  return {
    default: {
      create: () => ({
        request,
        interceptors: {
          request: { use: dummyUse },
          response: { use: dummyUse },
        },
      }),
    },
  };
});

function getMockedRequest() {
  return (axios as any).create().request as ReturnType<typeof vi.fn>;
}

describe('AxiosHttpClient schema validation', () => {
  it('throws HttpError on invalid request body (requestSchema)', async () => {
    const client = new AxiosHttpClient();

    const requestSchema = z.object({
      email: z.string().email(),
      password: z.string().min(8),
    });

    const promise = client.request({
      method: 'POST',
      path: '/dummy',
      body: { email: 'not-an-email', password: 'short' },
      requestSchema,
    });

    await promise.catch((e) => {
      expect(e).toBeInstanceOf(HttpError);
      expect((e as HttpError).getCode()).toBe('REQUEST_VALIDATION');
    });
  });

  it('throws HttpError on invalid response body (responseSchema)', async () => {
    const mockedRequest = getMockedRequest();
    mockedRequest.mockResolvedValueOnce({ data: { ok: false } });

    const client = new AxiosHttpClient();

    const responseSchema = z.object({ success: z.literal(true) });

    const promise = client.request({
      method: 'GET',
      path: '/dummy',
      responseSchema,
    });

    await promise.catch((e) => {
      expect(e).toBeInstanceOf(HttpError);
      expect((e as HttpError).getCode()).toBe('RESPONSE_VALIDATION');
    });
  });

  it('passes through when schemas are satisfied', async () => {
    const mockedRequest = getMockedRequest();
    mockedRequest.mockResolvedValueOnce({ data: { success: true } });

    const client = new AxiosHttpClient();

    const responseSchema = z.object({ success: z.literal(true) });

    const result = await client.request({
      method: 'GET',
      path: '/dummy',
      responseSchema,
    });

    expect(result).toEqual({ success: true });
  });
});
