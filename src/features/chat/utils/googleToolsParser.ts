export interface CalendarEvent {
  id: string
  summary?: string
  description?: string
  start?: string
  end?: string
  location?: string
  attendees?: Array<{ email: string; displayName?: string }>
  htmlLink?: string
  status?: string
}

export interface EmailMessage {
  id: string
  subject?: string
  from?: string
  to?: string
  date?: string
  snippet?: string
  body?: string
  isRead?: boolean
  isImportant?: boolean
  hasAttachments?: boolean
  labels?: string[]
  webLink?: string
}

interface ParsedToolResult {
  type: 'calendar' | 'gmail' | 'text'
  title: string
  data?: CalendarEvent[] | EmailMessage[]
  rawContent?: string
}

/**
 * Google Tools의 결과를 파싱하여 UI에 적합한 형태로 변환합니다.
 */
export function parseGoogleToolResult(toolCall: string, toolResult: any, content: string): ParsedToolResult {
  try {
    
    // Calendar 도구들 처리
    if (toolCall === 'get_calendar_events') {
      return parseCalendarResult(toolResult, content)
    }
    
    // Gmail 도구들 처리
    if (toolCall === 'get_emails') {
      return parseGmailResult(toolResult, content)
    }
    
    // 기타 도구들은 일반 텍스트로 처리
    return {
      type: 'text',
      title: getToolDisplayName(toolCall),
      rawContent: content
    }
    
  } catch (error) {
    console.warn('Failed to parse Google tool result:', error)
    return {
      type: 'text',
      title: getToolDisplayName(toolCall),
      rawContent: content
    }
  }
}

function parseCalendarResult(toolResult: any, content: string): ParsedToolResult {
  const events: CalendarEvent[] = []
  
  // toolResult가 배열 형태인지 확인
  if (Array.isArray(toolResult)) {
    events.push(...toolResult.map(parseCalendarEvent))
  } else if (toolResult && typeof toolResult === 'object') {
    // 단일 이벤트 또는 events 속성을 가진 객체
    if (toolResult.events && Array.isArray(toolResult.events)) {
      events.push(...toolResult.events.map(parseCalendarEvent))
    } else if (toolResult.id) {
      // 단일 이벤트
      events.push(parseCalendarEvent(toolResult))
    }
  }
  
  // 콘텐츠에서 이벤트 정보 추출 시도 (fallback)
  if (events.length === 0) {
    const extractedEvents = extractEventsFromContent(content)
    events.push(...extractedEvents)
  }
  
  // 시작 시간 기준으로 정렬
  events.sort((a, b) => {
    if (!a.start || !b.start) return 0
    return new Date(a.start).getTime() - new Date(b.start).getTime()
  })
  
  return {
    type: 'calendar',
    title: '캘린더 일정',
    data: events
  }
}

function parseGmailResult(toolResult: any, content: string): ParsedToolResult {
  const emails: EmailMessage[] = []
  
  // toolResult가 배열 형태인지 확인
  if (Array.isArray(toolResult)) {
    emails.push(...toolResult.map(parseEmailMessage))
  } else if (toolResult && typeof toolResult === 'object') {
    // 단일 메일 또는 messages 속성을 가진 객체
    if (toolResult.messages && Array.isArray(toolResult.messages)) {
      emails.push(...toolResult.messages.map(parseEmailMessage))
    } else if (toolResult.id) {
      // 단일 메일
      emails.push(parseEmailMessage(toolResult))
    }
  }
  
  // 콘텐츠에서 메일 정보 추출 시도 (fallback)
  if (emails.length === 0) {
    const extractedEmails = extractEmailsFromContent(content)
    emails.push(...extractedEmails)
  }
  
  // 날짜 기준으로 최신순 정렬
  emails.sort((a, b) => {
    if (!a.date || !b.date) return 0
    return new Date(b.date).getTime() - new Date(a.date).getTime()
  })
  
  return {
    type: 'gmail',
    title: 'Gmail 메일',
    data: emails
  }
}

function parseCalendarEvent(eventData: any): CalendarEvent {
  // time 필드가 있는 경우 파싱 (예: "07/24 18:00 - 20:00")
  let startTime, endTime
  if (eventData.time) {
    const timeParts = eventData.time.split(' - ')
    if (timeParts.length === 2) {
      // 현재 년도 추가하여 파싱
      const currentYear = new Date().getFullYear()
      const [startPart, endPart] = timeParts
      
      // "07/24 18:00" 형식 파싱
      if (startPart.includes('/')) {
        const [datePart, timePart] = startPart.split(' ')
        const [month, day] = datePart.split('/')
        startTime = new Date(`${currentYear}-${month.padStart(2, '0')}-${day.padStart(2, '0')}T${timePart}:00+09:00`).toISOString()
        
        // 종료 시간은 같은 날짜에 시간만 다름
        if (endPart.includes(':')) {
          endTime = new Date(`${currentYear}-${month.padStart(2, '0')}-${day.padStart(2, '0')}T${endPart}:00+09:00`).toISOString()
        }
      }
    }
  }

  return {
    id: eventData.id || generateId(),
    summary: eventData.summary || eventData.title,
    description: eventData.description,
    start: startTime || eventData.start?.dateTime || eventData.start?.date || eventData.start,
    end: endTime || eventData.end?.dateTime || eventData.end?.date || eventData.end,
    location: eventData.location,
    attendees: eventData.attendees,
    htmlLink: eventData.htmlLink,
    status: eventData.status
  }
}

function parseEmailMessage(emailData: any): EmailMessage {
  return {
    id: emailData.id || generateId(),
    subject: emailData.subject,
    from: emailData.from,
    to: emailData.to,
    date: emailData.date || emailData.internalDate,
    snippet: emailData.snippet,
    body: emailData.body,
    isRead: emailData.labelIds ? !emailData.labelIds.includes('UNREAD') : true,
    isImportant: emailData.labelIds ? emailData.labelIds.includes('IMPORTANT') : false,
    hasAttachments: emailData.payload?.parts?.some((part: any) => part.filename && part.filename.length > 0) || false,
    labels: emailData.labelIds,
    webLink: emailData.webLink || `https://mail.google.com/mail/u/0/#inbox/${emailData.id}`
  }
}

function extractEventsFromContent(content: string): CalendarEvent[] {
  const events: CalendarEvent[] = []
  
  try {
    // JSON 코드 블록에서 데이터 추출
    const jsonBlockMatch = content.match(/```json\s*([\s\S]*?)\s*```/)
    if (jsonBlockMatch) {
      const jsonContent = jsonBlockMatch[1].trim()
      
      try {
        const jsonData = JSON.parse(jsonContent)
        
        if (Array.isArray(jsonData)) {
          // JSON 배열인 경우
          events.push(...jsonData.map(parseCalendarEvent))
        } else if (jsonData && typeof jsonData === 'object') {
          // 단일 객체인 경우
          events.push(parseCalendarEvent(jsonData))
        }
      } catch (jsonError) {
        // JSON 파싱 실패 시 조용히 무시
      }
    }
    
    // 기존 텍스트 패턴 매칭도 유지
    if (events.length === 0) {
      // "제목: 회의, 시간: 2025-07-23 14:00-15:00" 패턴
      const eventPattern = /제목:\s*([^,\n]+)[,\s]*시간:\s*([^,\n]+)/g
      let match
      
      while ((match = eventPattern.exec(content)) !== null) {
        const [, title, timeStr] = match
        
        events.push({
          id: generateId(),
          summary: title.trim(),
          start: parseTimeString(timeStr),
          description: '텍스트에서 추출된 일정'
        })
      }
    }
  } catch (error) {
    // 이벤트 추출 실패 시 조용히 무시
  }
  
  return events
}

function extractEmailsFromContent(content: string): EmailMessage[] {
  const emails: EmailMessage[] = []
  
  try {
    // JSON 코드 블록에서 데이터 추출
    const jsonBlockMatch = content.match(/```json\s*([\s\S]*?)\s*```/)
    if (jsonBlockMatch) {
      const jsonContent = jsonBlockMatch[1].trim()
      
      try {
        const jsonData = JSON.parse(jsonContent)
        
        if (Array.isArray(jsonData)) {
          // JSON 배열인 경우
          emails.push(...jsonData.map(parseEmailMessage))
        } else if (jsonData && typeof jsonData === 'object') {
          // 단일 객체인 경우
          emails.push(parseEmailMessage(jsonData))
        }
      } catch (jsonError) {
        // JSON 파싱 실패 시 조용히 무시
      }
    }
    
    // 기존 텍스트 패턴 매칭도 유지
    if (emails.length === 0) {
      // 스크린샷에서 보이는 패턴: "제목: "How else would...", 보낸 사람: The Substack Post, 받은 날짜: 2025년 7월 22일"
      const emailPattern1 = /제목:\s*"([^"]+)"\s*.*?보낸\s*사람:\s*([^\n,]+?)(?:\s+([^\n,]+@[^\s,]+))?\s*.*?받은\s*날짜:\s*([^\n]+)/gs
      let match
      
      while ((match = emailPattern1.exec(content)) !== null) {
        const [, subject, senderName, senderEmail, dateStr] = match
        const from = senderEmail ? `${senderName.trim()} <${senderEmail.trim()}>` : senderName.trim()
        
        emails.push({
          id: generateId(),
          subject: subject.trim(),
          from: from,
          snippet: '텍스트에서 추출된 메일',
          isRead: true,
          date: parseDateString(dateStr) || new Date().toISOString()
        })
      }
      
      // 더 간단한 패턴들도 시도
      if (emails.length === 0) {
        // "제목: ..., 보낸 사람: ..." 패턴
        const emailPattern2 = /제목:\s*"([^"]+)"[,\s]*.*?보낸\s*사람:\s*([^\n,]+)/g
        
        while ((match = emailPattern2.exec(content)) !== null) {
          const [, subject, from] = match
          
          emails.push({
            id: generateId(),
            subject: subject.trim(),
            from: from.trim(),
            snippet: '텍스트에서 추출된 메일',
            isRead: true,
            date: new Date().toISOString()
          })
        }
      }
      
      // "보낸 사람: ..., 제목: ..." 패턴
      if (emails.length === 0) {
        const emailPattern3 = /보낸\s*사람:\s*([^,\n]+)[,\s]*제목:\s*([^,\n]+)/g
        
        while ((match = emailPattern3.exec(content)) !== null) {
          const [, from, subject] = match
          
          emails.push({
            id: generateId(),
            subject: subject.trim(),
            from: from.trim(),
            snippet: '텍스트에서 추출된 메일',
            isRead: true,
            date: new Date().toISOString()
          })
        }
      }
    }
  } catch (error) {
    // 메일 추출 실패 시 조용히 무시
  }
  
  return emails
}

function parseTimeString(timeStr: string): string {
  // 다양한 시간 형식을 ISO string으로 변환
  try {
    // "2025-07-23 14:00" 형식
    if (/\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}/.test(timeStr)) {
      return new Date(timeStr).toISOString()
    }
    
    // "7월 23일 2시" 형식
    const koreanTimeMatch = timeStr.match(/(\d+)월\s*(\d+)일\s*(\d+)시/)
    if (koreanTimeMatch) {
      const [, month, day, hour] = koreanTimeMatch
      const year = new Date().getFullYear()
      return new Date(year, parseInt(month) - 1, parseInt(day), parseInt(hour)).toISOString()
    }
    
    return new Date().toISOString()
  } catch {
    return new Date().toISOString()
  }
}

function parseDateString(dateStr: string): string | null {
  // "2025년 7월 22일" 형식 파싱
  try {
    const koreanDateMatch = dateStr.match(/(\d{4})년\s*(\d+)월\s*(\d+)일/)
    if (koreanDateMatch) {
      const [, year, month, day] = koreanDateMatch
      return new Date(parseInt(year), parseInt(month) - 1, parseInt(day)).toISOString()
    }
    
    // ISO 형식이면 그대로 사용
    if (dateStr.includes('T') || dateStr.includes('-')) {
      return new Date(dateStr).toISOString()
    }
    
    return null
  } catch {
    return null
  }
}

function getToolDisplayName(toolCall: string): string {
  const displayNames: Record<string, string> = {
    'get_calendar_events': '캘린더 일정',
    'create_calendar_event': '일정 생성',
    'find_free_time': '빈 시간 찾기',
    'get_emails': 'Gmail 메일',
    'send_email': '메일 발송'
  }
  
  return displayNames[toolCall] || toolCall
}

function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}

/**
 * 메시지가 Google Tools 결과를 포함하고 있는지 확인합니다.
 */
export function hasGoogleToolResult(message: any): boolean {
  
  // toolResult가 없어도 Google 도구 호출이면 처리 시도
  return message.toolCall && 
         (message.toolStatus === 'completed' || message.toolStatus === 'error') && 
         ['get_calendar_events', 'get_emails', 'create_calendar_event', 'send_email', 'find_free_time'].includes(message.toolCall)
}

/**
 * Google Tools 결과인지 확인하고 파싱된 결과를 반환합니다.
 */
export function getGoogleToolResult(message: any): ParsedToolResult | null {
  if (!hasGoogleToolResult(message)) {
    return null
  }
  
  return parseGoogleToolResult(message.toolCall, message.toolResult, message.content)
}