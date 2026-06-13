import { useMemo } from 'react';
import { NodeKind, NodeStatus } from './types';
import { GraphData, ProcessedNode, ProcessedEdge } from './DependencyGraph3DTypes';

function getNodeColor(status: string | NodeStatus, kind: string | NodeKind): string {
    if (kind === NodeKind.PROJECT) return '#a855f7';
    if (kind === NodeKind.FOLDER) return '#e2e8f0';
    if (kind === NodeKind.EXTERNAL_PACKAGE) return '#3b82f6';
    
    switch (status) {
      case NodeStatus.VERIFIED: return '#22c55e';
      case NodeStatus.BROKEN: return '#ef4444';
      case NodeStatus.WARNING: return '#eab308';
      default: return '#94a3b8';
    }
}

export const useGraphData = (data: GraphData | null, filters: Record<string, boolean>) => {
  return useMemo(() => {
    if (!data) return { nodes: [], links: [] };

    // Filter nodes based on state
    const filteredNodes = data.nodes.filter(node => {
      if (node.kind === NodeKind.EXTERNAL_PACKAGE) return filters.EXTERNAL_PACKAGE;
      const statusKey = node.status as keyof typeof filters;
      return filters[statusKey] !== false;
    });

    const nodeIds = new Set(filteredNodes.map(n => n.id));

    // Filter edges to only include visible nodes
    const filteredEdges = data.edges.filter(edge => 
      nodeIds.has(edge.source) && nodeIds.has(edge.target)
    );

    const nodes: ProcessedNode[] = filteredNodes.map(node => ({
      ...node,
      name: node.label,
      val: node.kind === NodeKind.FOLDER || node.kind === NodeKind.PROJECT ? 20 : 5,
      color: getNodeColor(node.status, node.kind),
      neighbors: new Set<string>(),
      links: [] as ProcessedEdge[]
    }));

    const nodeMap = new Map<string, ProcessedNode>(nodes.map(n => [n.id, n]));

    const links: ProcessedEdge[] = filteredEdges.map(edge => {
        const isCycle = !!edge.is_cycle;
        const processedEdge: ProcessedEdge = {
            ...edge,
            isCycle: isCycle,
            color: isCycle ? '#ef4444' : (edge.status === NodeStatus.BROKEN ? '#ff4d4d' : '#4a5568'),
            width: isCycle ? 3 : (edge.status === NodeStatus.BROKEN ? 2 : 0.5)
        };
        
        const s = nodeMap.get(edge.source);
        const t = nodeMap.get(edge.target);
        if (s && t) {
          s.neighbors.add(t.id);
          t.neighbors.add(s.id);
          s.links.push(processedEdge);
          t.links.push(processedEdge);
        }
        return processedEdge;
    });

    return { nodes, links };
  }, [data, filters]);
};
