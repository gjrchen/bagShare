import React, { useEffect, useState } from "react";
import axios from "axios";
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import Grid from '@mui/material/Grid';
import { ToggleButton } from "@mui/material";
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { createTheme, ThemeProvider } from '@mui/material/styles';


const CheckOutTab = () => {

    const [selected, setSelected] = useState(false);
    const theme = createTheme();

  const handleSubmit = (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    let info = ({
      phonenumber: data.get('phonenumber'),
      password: data.get('pin'),
      creditcardinfo: data.get('credcard'),
      bag: data.get('bag'),
      first_time: selected
    });
    
    if (info.phonenumber.length !== 10 || info.password.length !== 4 || info.bag.length !== 8){
      alert ("NOT SUCCESSFUL! Please ensure all fields are filled correctly!")
    } 
    else if (info.first_time && info.creditcardinfo.length !== 16){
      alert("NOT SUCCESSFUL! Credit Card length is not valid!")
    }
    else {
      axios.post("http://127.0.0.1:5000/api/check_out_bag", {info} )
      .then((response) => {
        if (response.data === true){
          alert ("Success!")
          setTimeout(window.location.reload(false), 2000)
          console.log("success")
        }
        else{
          alert("Bag Checkout was NOT SUCCESSFUL! Retry, verify that internet connection is available and if problem persists, contact BagShare Support.");
        }});
    }  
  };


  return (
    <div className = "CheckOutTab">
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
            Check out bags (one at a time) here!
          </Typography>
          <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <ToggleButton
            value="check"
            selected={selected}
             onChange={() => {
                setSelected(!selected);
            }}
            >
            This is my first time using bag share with this phone number!
        
            </ToggleButton>
                
            <TextField
              margin="normal"
              required
              fullWidth
              id="phonenumber"
              label="Phone Number"
              name="phonenumber"
              type = "number"
              autoFocus
            />
            {!selected && (
            <div>
            <TextField
              margin="normal"
              required
              fullWidth
              name="pin"
              label="Enter your Account PIN"
              type="password"
              id="pin"
            />
            </div>
            )}
            
            {selected && (
            <div>
            <TextField
              margin="normal"
              required
              fullWidth
              name="pin"
              label="Create an Account PIN"
              type="number"
              id="pin"
            />

            <TextField
              margin="normal"
              required
              fullWidth
              name="credcard"
              label="Credit Card Number"
              type="number"
              id="credcard"
            />
            </div>
            )}

            <TextField
              margin="normal"
              required
              fullWidth
              name="bag"
              label="BAG ID (8 Digit)"
              type="number"
              id="bag"
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
            >
              Check Out Now
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


export default CheckOutTab;