import React, { useState } from "react";
import {
  Container,
  Box,
  Typography,
  Button,
  Input,
  CircularProgress,
  Alert,
  TextField,
} from "@mui/material";
import { styled } from "@mui/system";
import logImage from "./logo.svg";

const Root = styled(Container)(({ theme }) => ({
  textAlign: "center",
  padding: theme.spacing(3),
  backgroundColor: "#f0f0f0",
  minHeight: "100vh",
}));

const Header = styled(Box)(({ theme }) => ({
  backgroundColor: "#282c34",
  padding: theme.spacing(2),
  color: "white",
  borderRadius: "8px",
}));

const Form = styled("form")(({ theme }) => ({
  margin: theme.spacing(2, 0),
}));

const StyledInput = styled(Input)(({ theme }) => ({
  margin: theme.spacing(1, 0),
}));

const Image = styled("img")(({ theme }) => ({
  maxWidth: "100%",
  height: "auto",
  marginTop: theme.spacing(3),
  borderRadius: "10px",
}));

const DownloadLink = styled("a")({
  textDecoration: "none",
  color: "white",
});

const ResultsContainer = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(3),
  textAlign: "left",
}));

const ResultItem = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1),
  borderBottom: "1px solid #ccc",
}));

function App() {
  const [file, setFile] = useState(null);
  const [csvFileUrl, setCsvFileUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [searchKeyword, setSearchKeyword] = useState("");
  const [searchKeywordComponent, setSearchKeywordComponent] = useState("");
  const [startTime, setStartTime] = useState("00:00:00 01/01/00");
  const [endTime, setEndTime] = useState("23:59:59 31/12/99");

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("File upload failed");
      }

      const data = await response.json();
      setCsvFileUrl(data.csvFileUrl);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!csvFileUrl) {
      setError("Please upload a file first.");
      return;
    }

    setLoading(true);
    setError(null);

    const filename = csvFileUrl.split("/").pop();

    try {
      const response = await fetch("http://localhost:5000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          filename,
          keyword: searchKeyword,
          searchKeywordComponent,
          startTime,
          endTime,
        }),
      });

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data = await response.json();
      setSearchResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Root>
      <Header>
        <Typography variant="h4">Log to CSV Converter</Typography>
      </Header>
      <Form onSubmit={handleSubmit}>
        <StyledInput type="file" onChange={handleFileChange} disableUnderline />
        <Button
          variant="contained"
          color="primary"
          type="submit"
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : "Upload"}
        </Button>
      </Form>
      {error && <Alert severity="error">{error}</Alert>}
      {csvFileUrl && (
        <Box mt={2}>
          <Button variant="contained" color="secondary">
            <DownloadLink href={csvFileUrl} download="output.csv">
              Download CSV
            </DownloadLink>
          </Button>
        </Box>
      )}
      <Box mt={3}>
        <TextField
          label="Search Keyword in Message"
          value={searchKeyword}
          onChange={(e) => setSearchKeyword(e.target.value)}
          variant="outlined"
          fullWidth
          margin="normal"
        />
        <TextField
          label="Search Keyword for Component Name"
          value={searchKeywordComponent}
          onChange={(e) => setSearchKeywordComponent(e.target.value)}
          variant="outlined"
          fullWidth
          margin="normal"
        />
        <TextField
          label="Start Time (hh:mm:ss dd/mm/yy)"
          value={startTime}
          onChange={(e) => setStartTime(e.target.value)}
          variant="outlined"
          fullWidth
          margin="normal"
        />
        <TextField
          label="End Time (hh:mm:ss dd/mm/yy)"
          value={endTime}
          onChange={(e) => setEndTime(e.target.value)}
          variant="outlined"
          fullWidth
          margin="normal"
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleSearch}
          disabled={loading}
          style={{ marginTop: 20 }}
        >
          {loading ? <CircularProgress size={24} /> : "Search"}
        </Button>
      </Box>
      {searchResults.length > 0 && (
        <ResultsContainer>
          <Typography variant="h6">Search Results:</Typography>
          {searchResults.map((result, index) => (
            <ResultItem key={index}>
              <Typography variant="body2">
                <strong>Timestamp:</strong> {result.Timestamp}
              </Typography>
              <Typography variant="body2">
                <strong>Log Type:</strong> {result["Log Type"]}
              </Typography>
              <Typography variant="body2">
                <strong>Component Name:</strong> {result["Component Name"]}
              </Typography>
              <Typography variant="body2">
                <strong>Message:</strong> {result.Message}
              </Typography>
            </ResultItem>
          ))}
        </ResultsContainer>
      )}
      <Image src={logImage} alt="Log Processing" />
    </Root>
  );
}

export default App;
