export interface Counselor {
  id: number
  userId: number
  nickname: string
  avatar?: string
  title: string
  specialties: string
  yearsOfExperience: number
  introduction: string
  pricePerHour: number
  onlineStatus: number
  scheduleJson: string
  rating: number
  reviewCount: number
}

export interface Appointment {
  id: number
  userId: number
  userNickname?: string
  counselorId: number
  counselorUserId?: number
  counselorName?: string
  counselorTitle?: string
  counselorSpecialties?: string
  appointmentTime: string
  durationMinutes: number
  type: string
  issueDescription: string
  status: string
  reminderStatus?: string
  canChat?: boolean
}

export interface AssessmentScale {
  id: number
  name: string
  code: string
  description: string
  questionJson: string
}

export interface Article {
  id: number
  title: string
  category?: string
  summary?: string
  content: string
  authorName?: string
  status: string
  createdAt?: string
  updatedAt?: string
}

export interface AssessmentQuestion {
  id: string
  title: string
  description?: string
  type?: 'slider' | 'select'
  options?: Array<{ label: string; value: string | number }>
  min?: number
  max?: number
  step?: number
  reverse?: boolean
}

export interface RiskFactor {
  key: string
  name: string
  value: number
  contributionScore: number
  direction: string
  description: string
}

export interface AssessmentRecord {
  id: number
  scaleId: number
  score: number
  riskProbability: number
  resultLevel: string
  analysis: string
  modelName?: string
  leadingFactors?: RiskFactor[]
  createdAt: string
}

export interface AssessmentMonitorRecord {
  id: number
  userId: number
  username?: string
  nickname?: string
  scaleId: number
  scaleName?: string
  score?: number
  riskProbability?: number
  resultLevel?: string
  analysis?: string
  modelName?: string
  status?: string
  createdAt?: string
}

export interface DashboardRiskSlice {
  level: string
  count: number
}

export interface DashboardActivity {
  title: string
  description: string
  timestamp: string
}

export interface DashboardSummary {
  userCount: number
  counselorCount: number
  onlineCounselorCount: number
  appointmentCount: number
  pendingAppointmentCount: number
  assessmentCount: number
  highRiskCount: number
  riskDistribution: DashboardRiskSlice[]
  recentActivities: DashboardActivity[]
}

export interface ChatMessage {
  id: number
  senderId: number
  receiverId: number
  content: string
  fileUrl?: string
  reviewStatus: string
}

export interface ChatContact {
  userId: number
  username?: string
  nickname?: string
  role?: string
  avatar?: string
  title?: string
  specialties?: string
}

export interface RegisterPayload {
  username: string
  password: string
  email: string
  phone: string
  nickname: string
  role: 'USER' | 'COUNSELOR'
  title?: string
  specialties?: string
  yearsOfExperience?: number
  introduction?: string
  pricePerHour?: number
}

export interface AdminUser {
  id: number
  username: string
  nickname?: string
  email?: string
  phone?: string
  role: string
  status: number
  gender?: string
  age?: number
  profile?: string
  title?: string
  specialties?: string
}

export interface NotificationItem {
  id: number
  targetUserId?: number
  targetRole?: string
  title?: string
  content?: string
  createdBy?: number
  createdAt?: string
}
