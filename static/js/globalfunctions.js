function convert_path_global_functions(ruta) {
    return ruta
        // Remove the trailing extension (e.g., .html) if it has one.
        .replace(/\.[^/.]+$/, "")

        // Replace backslashes (\) and slashes (/) with underscores (_)
        .replace(/[\\/]+/g, "_");
}

// create the variable global <AppFunctions> if not exist and create the object
window.Plus = window.Plus || {};
Plus.Functions = {
    modules: {},
    /**
     * @param {string} namespace
     * The unique namespace that identifies the JavaScript file.
     * Usually generated from the file path inside the ERP, for example:
     * "apps_customers_views_form".
     *
     * @param {string} name
     * The name used to register the function inside the namespace.
     * This name is later used to retrieve and execute the function.
     *
     * @param {Function} fn
     * The function to register in the global registry.
     */

    //in this function we will to save the function of the script 
    //use the <id> global of plus that was create in the backend
    define(namespace, name, fn) {
        namespace=convert_path_global_functions(namespace)
        if (!this.modules[namespace]) {
            this.modules[namespace] = {};
        }
        this.modules[namespace][name] = fn;
    },

    //in this function are get a function in specific use the namespace
    get(namespace) {
        namespace=convert_path_global_functions(namespace)
        if (this.modules[namespace]) {
            return this.modules[namespace];
        }

        console.warn(`Module '${namespace}' not found.`);
        return {};
    },


    /**
    * Deletes functions. If you pass a namespace, deletes only that module.
    * If you don't pass anything, resets the entire function registry.
    */
    reset(namespace = null) {
        if (namespace) {
            namespace = convert_path_global_functions(namespace);
            delete this.modules[namespace];
        } else {
            this.modules = {};
        }
    }
};

Plus.variables = {
    /**
     * Registers a variable reference inside the global PLUS ERP registry.
     *
     * Instead of storing the variable value, this method stores an object
     * reference. This allows the latest value to be retrieved at any time,
     * even if the variable changes after being registered.
     *
     * @param {string} namespace
     * Unique identifier of the JavaScript module.
     *
     * @param {string} variable_name
     * Name used to register the variable inside the module.
     *
     * @param {Object} refObj
     * Object containing the variable reference.
     * Example: { value: myVariable }
     */
    registry: {},

    // Función para registrar una variable por referencia (usando un objeto contenedor)
    define: function(namespace, variable_name, refObj) {
        namespace=convert_path_global_functions(namespace)
        if (!this.registry[namespace]) {
            this.registry[namespace] = {};
        }

        // save the reference complete of the object 
        this.registry[namespace][variable_name] = refObj;
    },

    // Función tercera para obtener el valor actualizado en tiempo real
    get: function(namespace, variable_name) {
        namespace=convert_path_global_functions(namespace)
        if (this.registry[namespace] && this.registry[namespace][variable_name]) {
            // Retorna siempre la propiedad .value actualizada
            return this.registry[namespace][variable_name].value;
        }
        console.warn(`No se encontró la variable '${variable_name}' para la clave '${namespace}'`);
        return null;
    },

    /**
    * Deletes variables. If you pass a namespace, deletes only that module.
    * If you don't pass anything, resets the entire variable registry.
    */
    reset(namespace = null) {
        if (namespace) {
            namespace = convert_path_global_functions(namespace);
            delete this.registry[namespace];
        } else {
            this.registry = {};
        }
    }
};
//  apps\contract\views\home.html



// ---  JS encapsulation ---
(()=>{
    //this variable is for can render all the container
    //this variable are remplace when the server run and load all the container
    const namespace = "{plus}";
    
    //here your create a function encapsulated
    function render_canva() {
        console.log("¡Ejecutando render_canva desde la clave {plus}!");
    }

    // save the function in the variable globale <AppFunctions> for after use in other scripts 
    window.Plus.Functions.define(namespace, "render", render_canva);
    window.Plus.Functions.get(namespace).create(); //here we run a function in specific
})();
