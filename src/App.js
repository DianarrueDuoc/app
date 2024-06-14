import React, { useState } from 'react';
import { Button, Container, Typography, Box, Input, Alert } from '@mui/material';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { db } from './firebase';
import { collection, addDoc } from 'firebase/firestore';
import './App.css';

function App() {
    const [file, setFile] = useState(null);
    const [summary, setSummary] = useState('');
    const [imagePaths, setImagePaths] = useState([]);
    const [successMessage, setSuccessMessage] = useState('');
    const [errorMessage, setErrorMessage] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setSuccessMessage('');
        setErrorMessage('');
        console.log("File selected:", e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            setErrorMessage("Please select a file first");
            return;
        }
        console.log("Starting upload...");
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://127.0.0.1:5000/process_pdf', {
                method: 'POST',
                body: formData
            });

            console.log("Response received:", response);
            const data = await response.json();
            console.log("Data received:", data);

            if (data.summary && data.image_paths) {
                setSummary(data.summary);
                setImagePaths(data.image_paths.map(path => path.split('/').pop())); // Extract filename

                // Save to Firestore
                try {
                    const docRef = await addDoc(collection(db, "uploads"), {
                        summary: data.summary,
                        imagePaths: data.image_paths
                    });
                    console.log("Document written with ID: ", docRef.id);
                    setSuccessMessage('File uploaded and data saved successfully!');
                    setErrorMessage('');
                } catch (e) {
                    console.error("Error adding document: ", e);
                    setErrorMessage('Error saving data to Firestore');
                    setSuccessMessage('');
                }
            } else {
                console.error("Error in response data:", data);
                setErrorMessage('Error processing the file');
                setSuccessMessage('');
            }
        } catch (error) {
            console.error("Error uploading file:", error);
            setErrorMessage('Error uploading the file');
            setSuccessMessage('');
        }
    };

    const appStyle = {
        backgroundImage: `url(${process.env.PUBLIC_URL + '/background.jpg'})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'column',
        textAlign: 'center',
        fontFamily: 'Caveat, cursive',
    };

    return (
        <Router>
            <div style={appStyle}>
                <Container maxWidth="sm">
                    <Routes>
                        <Route
                            path="/"
                            element={
                                <Box my={4} bgcolor="rgba(255, 255, 255, 0.8)" p={4} borderRadius={4} boxShadow={3}>
                                    <Typography variant="h4" component="h1" gutterBottom style={{ color: '#ff69b4' }}>
                                        Sube tu PDF
                                    </Typography>
                                    <Input type="file" onChange={handleFileChange} style={{ display: 'none' }} id="file-upload" />
                                    <label htmlFor="file-upload" style={{ margin: '20px', display: 'inline-block', padding: '10px 20px', backgroundColor: '#ff69b4', color: 'white', borderRadius: '5px', cursor: 'pointer' }}>
                                        Elegir archivo
                                    </label>
                                    <Button variant="contained" color="primary" onClick={handleUpload} style={{ marginTop: 10 }}>
                                        Subir
                                    </Button>
                                    {successMessage && <Alert severity="success" style={{ marginTop: 10 }}>{successMessage}</Alert>}
                                    {errorMessage && <Alert severity="error" style={{ marginTop: 10 }}>{errorMessage}</Alert>}
                                    {summary && (
                                        <Box my={2}>
                                            <Typography variant="h6">Resumen:</Typography>
                                            <Typography>{summary}</Typography>
                                        </Box>
                                    )}
                                    <Box my={2} className="pdf-image-container">
                                        {imagePaths.map((filename, index) => (
                                            <Box key={index} my={2}>
                                                <Typography variant="h6">
                                                    <Link to={`/image/${index + 1}`}>Generado {index + 1}</Link>
                                                </Typography>
                                            </Box>
                                        ))}
                                    </Box>
                                </Box>
                            }
                        />
                        {imagePaths.map((filename, index) => (
                            <Route
                                key={index}
                                path={`/image/${index + 1}`}
                                element={
                                    <Box my={4} bgcolor="rgba(255, 255, 255, 0.8)" p={4} borderRadius={4} boxShadow={3}>
                                        <Typography variant="h6">Generado {index + 1}</Typography>
                                        <img src={`http://127.0.0.1:5000/generated_images/${filename}`} alt={`Generado ${index + 1}`} />
                                        <Box mt={2}>
                                            <Link to="/">Volver a la lista</Link>
                                        </Box>
                                    </Box>
                                }
                            />
                        ))}
                    </Routes>
                </Container>
            </div>
        </Router>
    );
}

export default App;
