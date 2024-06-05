import { reuleaux, quantum } from 'ldrs'
import React from 'react';

const Loader = () => {
    quantum.register()
    return (
        <div className='loader'>
            <l-quantum
            size="111"
            speed="2.17" 
            color="black" 
            ></l-quantum>
        </div>
    )
}

export default Loader;