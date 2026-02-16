/**
 * Call Graph Tab Component
 * Sprint 7: Visualize function calls and dependencies
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Chip,
  List,
  ListItem,
  ListItemText,
  Grid,
  Paper,
} from '@mui/material';
import {
  AccountTree,
  Delete,
  Link,
  Warning,
  Info,
} from '@mui/icons-material';
import callGraphApi, {
  CallGraph,
  DependencyGraph,
  DeadCodeAnalysis,
  CircularDependencies,
} from '../services/callGraphApi';
import DependencyGraph from './DependencyGraph';

interface CallGraphTabProps {
  repositoryId: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const CallGraphTab: React.FC<CallGraphTabProps> = ({ repositoryId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);

  const [callGraph, setCallGraph] = useState<CallGraph | null>(null);
  const [dependencies, setDependencies] = useState<DependencyGraph | null>(null);
  const [deadCode, setDeadCode] = useState<DeadCodeAnalysis | null>(null);
  const [circularDeps, setCircularDeps] = useState<CircularDependencies | null>(
    null
  );

  useEffect(() => {
    loadData();
  }, [repositoryId]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load all data in parallel
      const [callGraphData, depsData, deadCodeData, circularData] =
        await Promise.all([
          callGraphApi.getCallGraph(repositoryId),
          callGraphApi.getDependencies(repositoryId),
          callGraphApi.getDeadCode(repositoryId),
          callGraphApi.getCircularDependencies(repositoryId),
        ]);

      setCallGraph(callGraphData);
      setDependencies(depsData);
      setDeadCode(deadCodeData);
      setCircularDeps(circularData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load call graph data');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" py={8}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ my: 2 }}>
        {error}
      </Alert>
    );
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      default:
        return 'info';
    }
  };

  return (
    <Box>
      {/* Summary Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <AccountTree sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h4">{callGraph?.total_functions || 0}</Typography>
            <Typography variant="body2" color="textSecondary">
              Functions
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Link sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
            <Typography variant="h4">{callGraph?.total_calls || 0}</Typography>
            <Typography variant="body2" color="textSecondary">
              Function Calls
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Delete sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
            <Typography variant="h4">{deadCode?.total_dead || 0}</Typography>
            <Typography variant="body2" color="textSecondary">
              Dead Functions
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Warning sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
            <Typography variant="h4">{circularDeps?.total_cycles || 0}</Typography>
            <Typography variant="body2" color="textSecondary">
              Circular Dependencies
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Card>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<AccountTree />} label="Call Graph" />
          <Tab icon={<Link />} label="Dependencies" />
          <Tab icon={<Delete />} label="Dead Code" />
          <Tab icon={<Warning />} label="Circular Dependencies" />
        </Tabs>

        <CardContent>
          {/* Tab 1: Call Graph Visualization */}
          <TabPanel value={tabValue} index={0}>
            {callGraph && callGraph.nodes.length > 0 ? (
              <Box>
                <Alert severity="info" sx={{ mb: 3 }}>
                  <strong>Interactive Call Graph:</strong> Nodes represent functions,
                  arrows show who calls whom. Blue = internal, gray = external
                  libraries.
                </Alert>
                <DependencyGraph
                  nodes={callGraph.nodes.map((n) => ({
                    id: n.name,
                    label: n.name,
                    type: n.is_external ? 'external' : 'internal',
                    file: n.file,
                  }))}
                  edges={callGraph.edges.map((e) => ({
                    source: e.from,
                    target: e.to,
                    label: `Line ${e.line}`,
                  }))}
                />

                {/* Function List */}
                <Box sx={{ mt: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    Function Details ({callGraph.nodes.length})
                  </Typography>
                  <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                    {callGraph.nodes.slice(0, 50).map((node) => (
                      <ListItem key={node.name} divider>
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="body1">{node.name}</Typography>
                              {node.is_external && (
                                <Chip label="External" size="small" />
                              )}
                            </Box>
                          }
                          secondary={
                            <>
                              {node.file && (
                                <Typography variant="caption" display="block">
                                  📄 {node.file}
                                </Typography>
                              )}
                              <Typography variant="caption">
                                Calls: {node.calls.length} | Called by:{' '}
                                {node.called_by.length}
                              </Typography>
                            </>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                  {callGraph.nodes.length > 50 && (
                    <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
                      Showing first 50 of {callGraph.nodes.length} functions
                    </Typography>
                  )}
                </Box>
              </Box>
            ) : (
              <Alert severity="info">
                No function calls detected. Make sure your repository contains
                analyzable code (Python, C, Assembly, or COBOL).
              </Alert>
            )}
          </TabPanel>

          {/* Tab 2: File Dependencies */}
          <TabPanel value={tabValue} index={1}>
            {dependencies && dependencies.files.length > 0 ? (
              <Box>
                <Alert severity="info" sx={{ mb: 3 }}>
                  <strong>File Dependencies:</strong> Shows which files import/include
                  other files. Supports Python imports, C includes, Assembly includes,
                  and COBOL COPY statements.
                </Alert>

                <Typography variant="h6" gutterBottom>
                  Files ({dependencies.total_files}) • Dependencies (
                  {dependencies.total_dependencies})
                </Typography>

                <List sx={{ maxHeight: 500, overflow: 'auto' }}>
                  {dependencies.files.map((file) => (
                    <ListItem key={file.file} divider>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="body1">{file.file}</Typography>
                            <Chip label={file.language} size="small" />
                          </Box>
                        }
                        secondary={
                          <Box sx={{ mt: 1 }}>
                            {file.imports.length > 0 && (
                              <Typography variant="caption" display="block">
                                📥 Imports: {file.imports.join(', ')}
                              </Typography>
                            )}
                            {file.imported_by.length > 0 && (
                              <Typography variant="caption" display="block">
                                📤 Imported by: {file.imported_by.length} file(s)
                              </Typography>
                            )}
                            {file.imports.length === 0 &&
                              file.imported_by.length === 0 && (
                                <Typography variant="caption" color="textSecondary">
                                  No dependencies
                                </Typography>
                              )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            ) : (
              <Alert severity="info">
                No dependencies detected in this repository.
              </Alert>
            )}
          </TabPanel>

          {/* Tab 3: Dead Code */}
          <TabPanel value={tabValue} index={2}>
            {deadCode && deadCode.dead_functions.length > 0 ? (
              <Box>
                <Alert severity="warning" sx={{ mb: 3 }}>
                  <strong>Dead Code Detected:</strong> These functions are never called.
                  Consider removing them to improve code quality.
                </Alert>

                <Typography variant="h6" gutterBottom>
                  Dead Functions ({deadCode.total_dead})
                </Typography>

                <List>
                  {deadCode.dead_functions.map((func, idx) => (
                    <ListItem key={idx} divider>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="body1">{func.name}</Typography>
                            <Chip
                              label={func.severity.toUpperCase()}
                              size="small"
                              color={getSeverityColor(func.severity) as any}
                            />
                          </Box>
                        }
                        secondary={
                          <>
                            <Typography variant="caption" display="block">
                              📄 {func.file}
                            </Typography>
                            <Typography variant="caption">
                              Makes {func.calls} call(s) but is never called
                            </Typography>
                          </>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            ) : (
              <Alert severity="success">
                <Typography variant="body1">
                  ✅ No dead code detected! All functions are being used.
                </Typography>
              </Alert>
            )}
          </TabPanel>

          {/* Tab 4: Circular Dependencies */}
          <TabPanel value={tabValue} index={3}>
            {circularDeps && circularDeps.circular_dependencies.length > 0 ? (
              <Box>
                <Alert severity="error" sx={{ mb: 3 }}>
                  <strong>Circular Dependencies Found:</strong> Functions calling each
                  other in a cycle. This can lead to infinite recursion and makes code
                  harder to understand.
                </Alert>

                <Typography variant="h6" gutterBottom>
                  Circular Dependencies ({circularDeps.total_cycles})
                </Typography>

                <List>
                  {circularDeps.circular_dependencies.map((cycle, idx) => (
                    <ListItem key={idx} divider>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="body1">
                              Cycle {idx + 1} ({cycle.length} functions)
                            </Typography>
                            <Chip
                              label={cycle.severity.toUpperCase()}
                              size="small"
                              color={getSeverityColor(cycle.severity) as any}
                            />
                          </Box>
                        }
                        secondary={
                          <Typography variant="caption">
                            {cycle.cycle.join(' → ')}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            ) : (
              <Alert severity="success">
                <Typography variant="body1">
                  ✅ No circular dependencies detected! Your call graph is acyclic.
                </Typography>
              </Alert>
            )}
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CallGraphTab;
