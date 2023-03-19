import React, { useEffect, useState } from "react";
import axios from "axios";
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { createTheme, ThemeProvider } from '@mui/material/styles';


const ReturnTab = () => {
   
    const theme = createTheme();

    const handleSubmit = (event) => {
        event.preventDefault();
        const data = new FormData(event.currentTarget);
        let bag = (
          data.get('bagid')
        );
        if (bag.length !== 8){
            alert ("RETURN UNSUCCESSFUL! Bag ID invalid length, should be 8. Retry...")
        } else {
            axios.post("http://127.0.0.1:5000/api/return_bag", {bag} )
            .then((response) => {
            if (response.data === true){
            alert ("Success!")
            setTimeout(window.location.reload(false), 2000)
            console.log("success")
            }
            else if (response.data === "bagnotout"){
            alert ("NOT SUCCESSFUL! This bag is not taken out. Ensure ID is correct.")
            }
            else if (response.data === "bagdoesntexist"){
                alert ("NOT SUCCESSFUL! This bag ID does not exist. Ensure ID is correct.")
                }
            else{
            alert("Bag Checkout was NOT SUCCESSFUL! Retry, verify that internet connection is available and if problem persists, contact BagShare Support.");
            }});
        }
    }

  return (
    <div className = "ReturnTab">
    <ThemeProvider theme={theme}>
      <Container component="main" maxWidth="xs">
        <CssBaseline />
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
         
          <Typography component="h3" variant="h5">
            Return bags (one at a time) here!
          </Typography>
          <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                
            <TextField
              margin="normal"
              required
              fullWidth
              id="bagid"
              label="Insert the Bag ID (8 digit)"
              name="bagid"
              type = "number"
              autoFocus
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
            >
              Return Now
            </Button>
            <Grid container>
              <Grid item xs>
              </Grid>
              <Grid item>
              </Grid>
            </Grid>
          </Box>
        </Box>
      </Container>
    </ThemeProvider>
    </div>
  );


};

export default ReturnTab;