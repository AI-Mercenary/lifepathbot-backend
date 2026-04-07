import mongoose from 'mongoose';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const clearSuggestions = async () => {
    try {
        console.log('Connecting to MongoDB...');
        await mongoose.connect(process.env.MONGO_URI);
        console.log('Connected.');
        
        console.log('Purging the Suggestions collection...');
        const result = await mongoose.connection.collection('suggestions').deleteMany({});
        
        console.log(`Successfully deleted ${result.deletedCount} suggestions!`);
        process.exit(0);
    } catch (error) {
        console.error('Error clearing data:', error);
        process.exit(1);
    }
};

clearSuggestions();
