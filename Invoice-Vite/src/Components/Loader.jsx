import { reuleaux, quantum, bouncy } from 'ldrs'
import React from 'react';

const Loader = () => {
    // quantum.register()
    bouncy.register()
    return (
            <l-bouncy
            size="20"
            speed="0.8" 
            color="#000" 
            ></l-bouncy>
    )
}


export default Loader;