import type {
  CoworkRoom,
  CoworkRoomSummary,
  LabsAnalytics,
  LabsOverview,
  Lesson,
  MicrosoftReadiness,
} from './types';

export interface ConnectorActionResult {
  title: string;
  summary: string;
  commands?: string[];
  next_steps?: string[];
  readiness?: unknown;
}

export function isSessionList(value: unknown): value is Lesson[];
export function isLabsOverview(value: unknown): value is LabsOverview;
export function isLabsAnalytics(value: unknown): value is LabsAnalytics;
export function isMicrosoftReadiness(value: unknown): value is MicrosoftReadiness;
export function isCoworkRoomsPayload(value: unknown): value is { rooms: CoworkRoomSummary[] };
export function hasCoworkRoomDetail(room: unknown): room is CoworkRoom;
export function isCoworkRoomDetailPayload(value: unknown, expectedRoomId: number): value is { room: CoworkRoom };
export function isConnectorActionResult(value: unknown): value is ConnectorActionResult;
