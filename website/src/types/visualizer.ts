// Types for the 3D Visualizer (simplified - single scene)

export interface CodeMetadata {
  code: string;
  key: string;
  name: string;
  version: string;
  documentType: string;
  sectionCount: number;
  tableCount: number;
  fileSize: number;
  fileSizeMB: number;
  topKeywords: string[];
  levelCounts: Record<string, number>;
}

export interface MetadataSummary {
  codes: CodeMetadata[];
  totalSections: number;
  totalTables: number;
  totalSize: number;
  totalSizeMB: number;
}
