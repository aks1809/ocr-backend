import bodyParser from 'body-parser';
import { createServer } from "http";
import { Server } from "socket.io";
import express from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';

const app = express();
const httpServer = createServer(app);
const PORT = 9000;

httpServer.listen(PORT, (err) => {
    if (err) {
        console.log("Cannot run!");
    } else {
        const dir = `uploads`;
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir);
        }
        console.log(`API server listening on port: ${PORT}`);
    }
});

export const io = new Server(httpServer, { cors: { origin: "*" } });

app.use(bodyParser.json());

// Set up multer for file upload
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        const timestamp = Date.now();
        const fileName = `${timestamp}-${file.originalname}`;
        cb(null, fileName);
    },
});

const upload = multer({ storage });

app.get('/preview/:name', (req, res) => {
    const imagePath = `${process.cwd()}/uploads/${req.params.name}`;
    res.sendFile(imagePath);
});

// Define an API route for image upload
app.post('/upload', upload.single('image'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ message: 'No image uploaded.' });
    }
    // Process the image (e.g., save it to a database or perform other operations)
    return res.status(200).json({ message: 'Image uploaded successfully.', filename: req.file.filename });
});

app.post('/analysis', (req, res) => {
    const { input_1_image, input_2_image, input_2_text } = req.body;
    io.sockets.emit("input", {
        input_1_image, input_2_image, input_2_text
    });
    return res.status(200).json({ message: 'Image uploaded successfully.' });
});

io.on("connection", (socket) => {
    socket.on("output", async (data) => {
        console.log(data);
        io.sockets.emit("frontend", data);
    });
});

export default app;
