import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Typography } from '@mui/material';

const Result = () => {
    const navigate = useNavigate();

    const goToHome = () => {
        navigate('/');
    };

    return (
        <div>
            <Typography variant="h4">Results</Typography>
            <Button onClick={goToHome}>Go Home</Button>
        </div>
    );
};

export default Result;