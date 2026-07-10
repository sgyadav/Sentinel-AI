import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../services/api";
import {
    connectWebSocket,
    closeWebSocket
} from "../services/websocket";

import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from "@mui/material";

function IncidentTable() {

  const navigate = useNavigate();

  const [incidents, setIncidents] = useState([]);

  const loadIncidents = async () => {

    try {

      const response = await api.get("/incidents");

      setIncidents(response.data);

    } catch (err) {

      console.log(err);

    }

  };

  useEffect(() => {

    loadIncidents();

    connectWebSocket((message) => {

        if (message.type === "incident") {

            setIncidents((previous) => [

                message.incident,

                ...previous

            ]);

        }

    });

    return () => {

        closeWebSocket();

    };

}, []);

  const getColor = (score) => {

    if (score >= 70) return "error";

    if (score >= 40) return "warning";

    return "success";

  };

  return (

    <Paper
      sx={{
        marginTop: 4,
        padding: 3
      }}
    >

      <Typography
        variant="h5"
        sx={{ mb: 2 }}
      >
        Live Security Incidents
      </Typography>

      <TableContainer>

        <Table>

          <TableHead>

            <TableRow>

              <TableCell><b>ID</b></TableCell>

              <TableCell><b>Hostname</b></TableCell>

              <TableCell><b>Attack</b></TableCell>

              <TableCell><b>Risk</b></TableCell>

              <TableCell><b>Status</b></TableCell>

              <TableCell><b>Recommendation</b></TableCell>

              <TableCell><b>Action</b></TableCell>

            </TableRow>

          </TableHead>

          <TableBody>

            {incidents.map((incident) => (

              <TableRow key={incident.incident_id}>

                <TableCell>

                  {incident.incident_id}

                </TableCell>

                <TableCell>

                  {incident.hostname}

                </TableCell>

                <TableCell>

                  {incident.attack_type}

                </TableCell>

                <TableCell>

                  <Chip
                    label={incident.risk_score}
                    color={getColor(incident.risk_score)}
                  />

                </TableCell>

                <TableCell>
  {incident.status}
</TableCell>

<TableCell>
  {incident.recommendation}
</TableCell>

<TableCell>
  <button
    onClick={() =>
      navigate(`/incident/${incident.incident_id}`)
    }
    style={{
      background: "#2563eb",
      color: "white",
      border: "none",
      padding: "8px 14px",
      borderRadius: "5px",
      cursor: "pointer"
    }}
  >
    View
  </button>
</TableCell>

              </TableRow>

            ))}

          </TableBody>

        </Table>

      </TableContainer>

    </Paper>

  );

}

export default IncidentTable;