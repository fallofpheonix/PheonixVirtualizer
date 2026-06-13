import React, { useEffect, useRef } from 'react';
import ForceGraph3D from '3d-force-graph';
import { ProcessedNode, ProcessedEdge } from './DependencyGraph3DTypes';
import { NodeKind } from './types';

interface SceneManagerProps {
  containerRef: React.RefObject<HTMLDivElement | null>;
  graphData: { nodes: ProcessedNode[], links: ProcessedEdge[] };
  selectedNode: ProcessedNode | null;
  hoverNode: ProcessedNode | null;
  onNodeClick: (node: any) => void;
  onNodeHover: (node: any) => void;
  graphRef: React.MutableRefObject<any>;
}

export const SceneManager: React.FC<SceneManagerProps> = ({
  containerRef, graphData, selectedNode, hoverNode, onNodeClick, onNodeHover, graphRef
}) => {
  useEffect(() => {
    if (!containerRef.current || !graphData.nodes.length) return;

    const Graph = ForceGraph3D()(containerRef.current)
      .graphData(graphData)
      .cooldownTicks(50)
      .nodeColor((node: any) => {
        const n = node as ProcessedNode;
        if (selectedNode || hoverNode) {
          const isNeighbor = (selectedNode?.neighbors?.has(n.id)) || (hoverNode?.neighbors?.has(n.id));
          const isSelected = selectedNode?.id === n.id || hoverNode?.id === n.id;
          return isSelected || isNeighbor ? n.color : 'rgba(63, 63, 70, 0.2)';
        }
        return n.color;
      })
      .nodeThreeObjectExtend(true)
      .nodeThreeObject(() => undefined)
      .linkColor((link: any) => {
        const l = link as ProcessedEdge;
        if (selectedNode || hoverNode) {
          const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
          const targetId = typeof l.target === 'string' ? l.target : l.target.id;
          const isRelated = selectedNode?.id === sourceId || selectedNode?.id === targetId ||
                           hoverNode?.id === sourceId || hoverNode?.id === targetId;
          return isRelated ? l.color : 'rgba(63, 63, 70, 0.1)';
        }
        return l.color;
      })
      .nodeVal((node: any) => {
        const n = node as ProcessedNode;
        if (n.kind === NodeKind.FOLDER || n.kind === NodeKind.PROJECT) return 20;
        const churn = n.metadata?.churn || 0;
        return 5 + Math.min(churn / 2, 15);
      })
      .linkLineDash((link: any) => (link as ProcessedEdge).isCycle ? [3, 2] : null)
      .linkDashOffset((link: any) => (link as ProcessedEdge).isCycle ? (Date.now() / 500) % 5 : 0)
      .linkWidth((link: any) => {
        const l = link as ProcessedEdge;
        if (selectedNode || hoverNode) {
          const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
          const targetId = typeof l.target === 'string' ? l.target : l.target.id;
          const isRelated = selectedNode?.id === sourceId || selectedNode?.id === targetId ||
                           hoverNode?.id === sourceId || hoverNode?.id === targetId;
          return isRelated ? (l.width * 2) : 0.2;
        }
        return l.width;
      })
      .linkOpacity(0.6)
      .nodeLabel((node: any) => `[${(node as ProcessedNode).kind}] ${(node as ProcessedNode).name}`)
      .onNodeClick(onNodeClick)
      .onNodeHover(onNodeHover);

    const renderer = Graph.renderer();
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    graphRef.current = Graph;

    const handleResize = () => {
      if (containerRef.current) {
        Graph.width(containerRef.current.clientWidth);
        Graph.height(containerRef.current.clientHeight);
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (containerRef.current) containerRef.current.innerHTML = '';
    };
  }, [graphData, selectedNode, hoverNode, onNodeClick, onNodeHover]);

  return null;
};
