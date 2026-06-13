import { NodeKind, NodeStatus } from './types';

export interface GraphNode {
  id: string;
  kind: NodeKind | string;
  label: string;
  status: NodeStatus | string;
  parentId?: string;
  val?: number;
  color?: string;
  metadata?: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationType: string;
  status: NodeStatus | string;
  is_cycle?: boolean;
  color?: string;
  width?: number;
  metadata?: Record<string, any>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  violations?: any[];
}

export interface ProcessedEdge extends GraphEdge {
  source: string | ProcessedNode;
  target: string | ProcessedNode;
  color: string;
  width: number;
  isCycle: boolean;
}

export interface ProcessedNode extends GraphNode {
  name: string;
  val: number;
  color: string;
  neighbors: Set<string>;
  links: ProcessedEdge[];
  x?: number;
  y?: number;
  z?: number;
}
