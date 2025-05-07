/**
 * Sample models for UniRig 3D viewer demonstration
 * 
 * This file provides examples of GLB models that can be loaded directly
 * into the model-viewer component for testing the interface.
 */

const sampleModels = [
    {
        name: "Astronaut",
        url: "https://modelviewer.dev/shared-assets/models/Astronaut.glb",
        thumbnail: "https://modelviewer.dev/shared-assets/models/Astronaut.webp"
    },
    {
        name: "Horse",
        url: "https://modelviewer.dev/shared-assets/models/Horse.glb",
        thumbnail: "https://modelviewer.dev/shared-assets/models/Horse.webp"
    },
    {
        name: "Lantern",
        url: "https://modelviewer.dev/shared-assets/models/glTF-Sample-Models/2.0/Lantern/glTF-Binary/Lantern.glb",
        thumbnail: "https://modelviewer.dev/assets/examples/lantern-0.webp"
    },
    {
        name: "Damaged Helmet",
        url: "https://modelviewer.dev/shared-assets/models/glTF-Sample-Models/2.0/DamagedHelmet/glTF-Binary/DamagedHelmet.glb",
        thumbnail: "https://modelviewer.dev/assets/examples/damaged-helmet-0.webp"
    }
];

// Function to load a sample model directly into the viewer
function loadSampleModel(index, targetViewer) {
    if (index >= 0 && index < sampleModels.length) {
        const model = sampleModels[index];
        
        // Get the model viewer element
        const modelViewer = document.getElementById(targetViewer);
        
        // Set the source URL
        modelViewer.src = model.url;
        
        // Show the model viewer and hide the empty state
        modelViewer.style.display = "block";
        const container = document.getElementById(`${targetViewer}Container`);
        if (container) {
            const emptyState = container.querySelector(".empty-viewer");
            if (emptyState) {
                emptyState.style.display = "none";
            }
        }
        
        return true;
    }
    return false;
}

// Function to create sample gallery UI
function createSampleGallery(containerId, targetViewer) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Create gallery HTML
    let galleryHTML = '<div class="sample-gallery">';
    
    // Add sample models
    sampleModels.forEach((model, index) => {
        galleryHTML += `
            <div class="sample-item" onclick="loadSampleModel(${index}, '${targetViewer}')">
                <img src="${model.thumbnail}" alt="${model.name}" />
                <div class="sample-name">${model.name}</div>
            </div>
        `;
    });
    
    galleryHTML += '</div>';
    
    // Add to container
    container.innerHTML = galleryHTML;
} 